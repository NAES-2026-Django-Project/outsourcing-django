from types import SimpleNamespace
from unittest import mock

import anthropic
import httpx2
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR
from accounts.tests import criar_usuario

from .markdown import markdown_seguro
from .models import ChamadaIA, ConfiguracaoIA, CotaUsuario, MensagemAssistente, Status
from .services import CotaExcedida, ErroIA, chamar_ia, janela_de_mensagens, testar_conexao

CHAVE = 'sk-ant-teste-1234567890abcd'


def resposta_falsa(texto='Resposta', stop_reason='end_turn', entrada=100, saida=20):
    return SimpleNamespace(
        content=[SimpleNamespace(type='thinking', thinking=''), SimpleNamespace(type='text', text=texto)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=entrada, output_tokens=saida, cache_creation_input_tokens=0, cache_read_input_tokens=0),
    )


def erro_de_conexao():
    return anthropic.APIConnectionError(request=httpx2.Request('POST', 'https://api.anthropic.com/v1/messages'))


@override_settings(ANTHROPIC_API_KEY='')
class BaseIA(TestCase):
    def setUp(self):
        self.dev = criar_usuario('dev@exemplo.com', DESENVOLVEDOR)
        self.admin = criar_usuario('admin@exemplo.com', ADMINISTRADOR)
        self.config = ConfiguracaoIA.carregar()
        self.config.definir_chave(CHAVE)
        self.config.save()
        patcher = mock.patch('ia.services.criar_cliente')
        self.criar_cliente = patcher.start()
        self.addCleanup(patcher.stop)
        self.api = self.criar_cliente.return_value.beta.messages.create
        self.api.return_value = resposta_falsa()

    def chamar(self, texto='Oi'):
        return chamar_ia(self.dev, [{'role': 'user', 'content': texto}], 'assistente', system='Sistema')


class ChamarIATests(BaseIA):
    def test_sucesso_e_auditado_com_tokens(self):
        chamada = self.chamar('Como mover?')
        self.assertEqual(chamada.resposta, 'Resposta')
        registro = ChamadaIA.objects.get()
        self.assertEqual((registro.status, registro.usuario, registro.pergunta), (Status.SUCESSO, self.dev, 'Como mover?'))
        self.assertEqual((registro.tokens_entrada, registro.tokens_saida, registro.total_tokens), (100, 20, 120))
        self.criar_cliente.assert_called_once_with(CHAVE)

    def test_parametros_enviados_a_api(self):
        self.chamar()
        kwargs = self.api.call_args.kwargs
        self.assertEqual(kwargs['model'], 'claude-opus-5-5')
        self.assertEqual(kwargs['output_config'], {'effort': 'low'})
        self.assertEqual(kwargs['system'], 'Sistema')
        self.assertEqual(kwargs['fallbacks'], 'default')
        self.assertEqual(kwargs['betas'], ['server-side-fallback-2026-07-01'])

    def test_haiku_nao_envia_fallback(self):
        self.config.modelo = 'claude-haiku-5-5'
        self.config.save()
        self.chamar()
        self.assertNotIn('fallbacks', self.api.call_args.kwargs)

    def test_cota_excedida_bloqueia_antes_da_api(self):
        ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.SUCESSO, tokens_entrada=200000)
        with self.assertRaises(CotaExcedida):
            self.chamar()
        self.api.assert_not_called()
        self.assertEqual(ChamadaIA.objects.filter(status=Status.BLOQUEADA).count(), 1)

    def test_cota_individual_substitui_a_padrao(self):
        CotaUsuario.objects.create(usuario=self.dev, limite_mensal=50)
        ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.SUCESSO, tokens_entrada=60)
        with self.assertRaises(CotaExcedida):
            self.chamar()

    def test_erro_da_api_e_auditado(self):
        self.api.side_effect = erro_de_conexao()
        with self.assertRaisesMessage(ErroIA, 'Não foi possível conectar'):
            self.chamar()
        registro = ChamadaIA.objects.get()
        self.assertEqual(registro.status, Status.ERRO)
        self.assertIn('APIConnectionError', registro.erro)

    def test_recusa_do_modelo_e_auditada(self):
        self.api.return_value = resposta_falsa(texto='', stop_reason='refusal')
        with self.assertRaises(ErroIA):
            self.chamar()
        self.assertEqual(ChamadaIA.objects.get().status, Status.RECUSADA)

    def test_ia_desativada_ou_sem_chave(self):
        self.config.ativo = False
        self.config.save()
        with self.assertRaisesMessage(ErroIA, 'desativado'):
            self.chamar()
        self.config.ativo = True
        self.config.definir_chave('')
        self.config.save()
        with self.assertRaisesMessage(ErroIA, 'não foi configurada'):
            self.chamar()
        self.api.assert_not_called()
        self.assertEqual(ChamadaIA.objects.filter(status=Status.ERRO).count(), 2)

    def test_chave_fica_cifrada_no_banco(self):
        bruto = ConfiguracaoIA.objects.values_list('chave_api_cifrada', flat=True).get()
        self.assertNotIn(CHAVE, bruto)
        self.assertEqual(ConfiguracaoIA.carregar().obter_chave(), CHAVE)
        self.assertEqual(ConfiguracaoIA.carregar().chave_mascarada, '••••abcd')

    def test_testar_conexao_audita_sem_gastar_tokens(self):
        self.criar_cliente.return_value.models.retrieve.return_value = SimpleNamespace(display_name='Claude Opus 5.5')
        sucesso, mensagem = testar_conexao(self.admin)
        self.assertTrue(sucesso)
        self.assertIn('Claude Opus 5.5', mensagem)
        registro = ChamadaIA.objects.get()
        self.assertEqual((registro.origem, registro.total_tokens), ('teste_conexao', 0))


class AssistenteTests(BaseIA):
    def perguntar(self, client=None, **extra):
        client = client or self.client
        return client.post(reverse('ia:perguntar'), {'pergunta': 'Pergunta nova'}, **extra)

    def test_janela_envia_apenas_as_ultimas_cinco_mensagens(self):
        for i in range(8):
            MensagemAssistente.objects.create(usuario=self.dev, papel='user', conteudo=f'P{i}')
            MensagemAssistente.objects.create(usuario=self.dev, papel='assistant', conteudo=f'R{i}')
        self.client.force_login(self.dev)
        self.perguntar()
        enviadas = self.api.call_args.kwargs['messages']
        self.assertEqual(len(enviadas), 5)
        self.assertEqual(enviadas[0]['role'], 'user')
        self.assertEqual([m['content'] for m in enviadas], ['P6', 'R6', 'P7', 'R7', 'Pergunta nova'])

    def test_janela_sempre_comeca_pelo_usuario(self):
        MensagemAssistente.objects.create(usuario=self.dev, papel='user', conteudo='P0')
        MensagemAssistente.objects.create(usuario=self.dev, papel='assistant', conteudo='R0')
        MensagemAssistente.objects.create(usuario=self.dev, papel='user', conteudo='P1')
        MensagemAssistente.objects.create(usuario=self.dev, papel='assistant', conteudo='R1')
        MensagemAssistente.objects.create(usuario=self.dev, papel='assistant', conteudo='R-extra')
        janela = janela_de_mensagens(self.dev, 'Nova')
        self.assertEqual(janela[0]['role'], 'user')
        self.assertLessEqual(len(janela), 5)

    def test_historico_e_por_usuario(self):
        MensagemAssistente.objects.create(usuario=self.admin, papel='user', conteudo='Do admin')
        self.assertEqual([m['content'] for m in janela_de_mensagens(self.dev, 'X')], ['X'])

    def test_system_inclui_instrucoes_e_contexto_do_projeto(self):
        self.client.force_login(self.dev)
        self.perguntar()
        system = self.api.call_args.kwargs['system']
        self.assertIn('Responda somente sobre o uso do sistema', system)
        self.assertIn('Apontamento de horas', system)
        self.assertIn('<contexto_do_sistema>', system)

    def test_resposta_grava_historico_e_volta_sanitizada(self):
        self.api.return_value = resposta_falsa('**Use o quadro** <script>alert(1)</script>')
        self.client.force_login(self.dev)
        dados = self.perguntar().json()
        self.assertIn('<strong>Use o quadro</strong>', dados['resposta_html'])
        self.assertNotIn('<script', dados['resposta_html'])
        self.assertEqual(dados['consumo'], 120)
        self.assertEqual(list(MensagemAssistente.objects.values_list('papel', flat=True)), ['user', 'assistant'])

    def test_erro_nao_grava_historico(self):
        self.api.side_effect = erro_de_conexao()
        self.client.force_login(self.dev)
        response = self.perguntar()
        self.assertEqual(response.status_code, 503)
        self.assertIn('erro', response.json())
        self.assertFalse(MensagemAssistente.objects.exists())

    def test_cota_excedida_retorna_429(self):
        CotaUsuario.objects.create(usuario=self.dev, limite_mensal=0)
        self.client.force_login(self.dev)
        self.assertEqual(self.perguntar().status_code, 429)

    def test_pergunta_vazia_ou_longa_e_recusada(self):
        self.client.force_login(self.dev)
        for texto in ['   ', 'x' * 2001]:
            with self.subTest(len(texto)):
                self.assertEqual(self.client.post(reverse('ia:perguntar'), {'pergunta': texto}).status_code, 400)
        self.api.assert_not_called()

    def test_post_sem_csrf_e_recusado(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.dev)
        self.assertEqual(self.perguntar(client).status_code, 403)
        self.api.assert_not_called()

    def test_post_com_csrf_por_ajax_e_aceito(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.dev)
        client.get(reverse('ia:meu_consumo'))
        token = client.cookies['csrftoken'].value
        response = self.perguntar(client, HTTP_X_CSRFTOKEN=token, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_get_nao_e_permitido(self):
        self.client.force_login(self.dev)
        self.assertEqual(self.client.get(reverse('ia:perguntar')).status_code, 405)

    def test_limpar_historico(self):
        MensagemAssistente.objects.create(usuario=self.dev, papel='user', conteudo='P')
        MensagemAssistente.objects.create(usuario=self.admin, papel='user', conteudo='Outro')
        self.client.force_login(self.dev)
        self.client.post(reverse('ia:limpar'))
        self.assertEqual(list(MensagemAssistente.objects.values_list('conteudo', flat=True)), ['Outro'])


class TelasIATests(BaseIA):
    rotas_admin = ['configuracao', 'requisicoes', 'uso_por_usuario']

    def test_anonimo_vai_ao_login(self):
        for nome in self.rotas_admin + ['meu_consumo']:
            with self.subTest(nome):
                self.assertIn(reverse('accounts:login'), self.client.get(reverse(f'ia:{nome}')).url)

    def test_desenvolvedor_recebe_403_nas_telas_administrativas(self):
        self.client.force_login(self.dev)
        for nome in self.rotas_admin:
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(f'ia:{nome}')).status_code, 403)
        self.assertEqual(self.client.post(reverse('ia:testar')).status_code, 403)

    def test_meu_consumo_mostra_somente_as_proprias_chamadas(self):
        ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.SUCESSO, tokens_entrada=300)
        ChamadaIA.objects.create(usuario=self.admin, origem='assistente', modelo='x', status=Status.SUCESSO, tokens_entrada=999)
        self.client.force_login(self.dev)
        response = self.client.get(reverse('ia:meu_consumo'))
        self.assertEqual(response.context['consumo'], 300)
        self.assertEqual(response.context['paginator'].count, 1)

    def test_administrador_ve_requisicoes_filtradas_e_detalhe(self):
        ok = ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.SUCESSO, resposta='**ok**')
        ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.ERRO)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('ia:requisicoes'), {'status': Status.SUCESSO})
        self.assertEqual(list(response.context['chamadas']), [ok])
        detalhe = self.client.get(reverse('ia:requisicao_detalhe', args=[ok.pk]))
        self.assertContains(detalhe, '<strong>ok</strong>', html=True)

    def test_uso_por_usuario_e_edicao_de_cota(self):
        ChamadaIA.objects.create(usuario=self.dev, origem='assistente', modelo='x', status=Status.SUCESSO, tokens_entrada=70, tokens_saida=30)
        self.client.force_login(self.admin)
        usuarios = {u.email: u for u in self.client.get(reverse('ia:uso_por_usuario')).context['usuarios']}
        self.assertEqual(usuarios['dev@exemplo.com'].tokens_mes, 100)
        self.assertEqual(usuarios['dev@exemplo.com'].limite, 200000)
        response = self.client.post(reverse('ia:cota_usuario', args=[self.dev.pk]), {'limite_mensal': 5000}, follow=True)
        self.assertContains(response, 'Cota do usuário atualizada.')
        self.assertEqual(CotaUsuario.objects.get(usuario=self.dev).limite_mensal, 5000)

    def test_configuracao_cifra_chave_nova_e_mantem_quando_vazia(self):
        self.client.force_login(self.admin)
        dados = {'ativo': 'on', 'modelo': 'claude-sonnet-5-5', 'esforco': 'medium', 'max_tokens': 4000,
                 'cota_mensal_padrao': 1000, 'instrucoes': 'Seja breve.', 'chave_api': ''}
        response = self.client.post(reverse('ia:configuracao'), dados, follow=True)
        self.assertContains(response, 'Configuração da IA salva.')
        self.assertNotContains(response, CHAVE)
        config = ConfiguracaoIA.carregar()
        self.assertEqual((config.modelo, config.obter_chave()), ('claude-sonnet-5-5', CHAVE))
        self.client.post(reverse('ia:configuracao'), {**dados, 'chave_api': 'sk-ant-nova-9999'})
        self.assertEqual(ConfiguracaoIA.carregar().obter_chave(), 'sk-ant-nova-9999')

    def test_botao_testar_conexao_mostra_resultado(self):
        self.criar_cliente.return_value.models.retrieve.side_effect = erro_de_conexao()
        self.client.force_login(self.admin)
        response = self.client.post(reverse('ia:testar'), follow=True)
        self.assertContains(response, 'Não foi possível conectar')


class MarkdownTests(TestCase):
    def test_remove_html_perigoso_e_mantem_formatacao(self):
        html = markdown_seguro('# Título\n\n- item\n\n[link](javascript:alert(1)) <img src=x onerror=alert(1)> <script>x</script>')
        self.assertIn('<li>item</li>', html)
        for proibido in ['<script', 'onerror', 'javascript:', '<img', '<h1']:
            with self.subTest(proibido):
                self.assertNotIn(proibido, html)
