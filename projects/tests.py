from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.messages import get_messages
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.views.defaults import bad_request, server_error

from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE
from accounts.tests import criar_usuario

from .models import Note, Project, Stage, Task, Team, TimeEntry
from .templatetags.paginacao import url_pagina


class Base(TestCase):
    def setUp(self):
        self.admin = criar_usuario('admin@exemplo.com', ADMINISTRADOR)
        self.gerente = criar_usuario('gerente@exemplo.com', GERENTE)
        self.outro_gerente = criar_usuario('outro@exemplo.com', GERENTE)
        self.dev = criar_usuario('dev@exemplo.com', DESENVOLVEDOR)
        self.estranho = criar_usuario('estranho@exemplo.com', DESENVOLVEDOR)
        self.equipe = Team.objects.create(name='Atlas', manager=self.gerente)
        self.equipe.members.add(self.dev)
        self.outra_equipe = Team.objects.create(name='Boreal', manager=self.outro_gerente)
        self.projeto = self.criar_projeto('Portal', self.equipe, self.gerente)
        self.projeto.assigned_members.add(self.dev)
        self.outro_projeto = self.criar_projeto('ERP', self.outra_equipe, self.outro_gerente)
        self.estagios = list(self.projeto.stages.all())
        self.tarefa = Task.objects.create(title='Login', stage=self.estagios[0])

    def criar_projeto(self, nome, equipe, dono):
        return Project.objects.create(name=nome, team=equipe, created_by=dono, start_date=date(2026, 11, 1))

    def mensagens(self, response):
        return [str(m) for m in get_messages(response.wsgi_request)]


class RegrasDeNegocioTests(Base):
    def test_projeto_nasce_com_quatro_estagios(self):
        self.assertEqual([e.order for e in self.estagios], [1, 2, 3, 4])

    def test_excluir_projeto_remove_estagios_e_tarefas(self):
        self.client.force_login(self.gerente)
        self.client.post(reverse('projects:projeto_excluir', args=[self.projeto.pk]))
        self.assertFalse(Project.objects.filter(pk=self.projeto.pk).exists())
        self.assertFalse(Task.objects.filter(pk=self.tarefa.pk).exists())

    def test_termino_nao_pode_ser_anterior_ao_inicio(self):
        self.client.force_login(self.gerente)
        response = self.client.post(reverse('projects:projeto_criar'), {
            'name': 'X', 'team': self.equipe.pk, 'start_date': '2026-11-10', 'end_date': '2026-11-01',
        })
        self.assertIn('end_date', response.context['form'].errors)

    def test_gerente_nao_cria_projeto_em_equipe_alheia(self):
        self.client.force_login(self.gerente)
        response = self.client.post(reverse('projects:projeto_criar'), {
            'name': 'X', 'team': self.outra_equipe.pk, 'start_date': '2026-11-10',
        })
        self.assertIn('team', response.context['form'].errors)

    def test_membro_atribuido_precisa_ser_da_equipe(self):
        self.client.force_login(self.gerente)
        response = self.client.post(reverse('projects:projeto_criar'), {
            'name': 'X', 'team': self.equipe.pk, 'start_date': '2026-11-10', 'assigned_members': [self.estranho.pk],
        })
        self.assertIn('assigned_members', response.context['form'].errors)

    def test_responsavel_precisa_participar_do_projeto(self):
        self.client.force_login(self.gerente)
        response = self.client.post(reverse('projects:tarefa_criar'), {
            'title': 'T', 'stage': self.estagios[0].pk, 'assigned_to': self.estranho.pk, 'priority': 'low',
        })
        self.assertIn('assigned_to', response.context['form'].errors)

    def test_estagio_com_tarefas_nao_e_excluido(self):
        self.client.force_login(self.gerente)
        response = self.client.post(reverse('projects:estagio_excluir', args=[self.estagios[0].pk]))
        self.assertTrue(Stage.objects.filter(pk=self.estagios[0].pk).exists())
        self.assertIn('Mova ou exclua as tarefas antes de excluir este estágio.', self.mensagens(response))

    def test_equipe_com_projetos_nao_e_excluida(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('projects:equipe_excluir', args=[self.equipe.pk]))
        self.assertTrue(Team.objects.filter(pk=self.equipe.pk).exists())
        self.assertIn('Este registro está em uso e não pode ser excluído.', self.mensagens(response))


class AcessoTests(Base):
    rotas_login = ['quadros', 'tarefas', 'anotacoes', 'projetos', 'estagios', 'equipes']

    def test_anonimo_e_redirecionado_ao_login(self):
        for nome in self.rotas_login:
            with self.subTest(nome):
                response = self.client.get(reverse(f'projects:{nome}'))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('accounts:login'), response.url)

    def test_desenvolvedor_recebe_403_em_views_de_gestao(self):
        self.client.force_login(self.dev)
        for nome in ['projetos', 'estagios', 'equipes', 'projeto_criar', 'equipe_criar']:
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(f'projects:{nome}')).status_code, 403)

    def test_gerente_nao_cadastra_equipe(self):
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.get(reverse('projects:equipe_criar')).status_code, 403)

    def test_gerente_ve_somente_equipes_que_gerencia(self):
        self.client.force_login(self.gerente)
        self.assertEqual(list(self.client.get(reverse('projects:equipes')).context['equipes']), [self.equipe])


class PosseProjetoTests(Base):
    def test_form_valid_grava_o_dono(self):
        self.client.force_login(self.gerente)
        self.client.post(reverse('projects:projeto_criar'), {'name': 'Novo', 'team': self.equipe.pk, 'start_date': '2026-11-10'})
        self.assertEqual(Project.objects.get(name='Novo').created_by, self.gerente)

    def test_lista_somente_os_proprios(self):
        self.client.force_login(self.gerente)
        self.assertEqual(list(self.client.get(reverse('projects:projetos')).context['projetos']), [self.projeto])

    def test_nao_dono_recebe_404(self):
        self.client.force_login(self.outro_gerente)
        for nome in ['projeto_detalhe', 'projeto_editar', 'projeto_excluir']:
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(f'projects:{nome}', args=[self.projeto.pk])).status_code, 404)

    def test_nao_dono_nao_exclui_por_post(self):
        self.client.force_login(self.outro_gerente)
        response = self.client.post(reverse('projects:projeto_excluir', args=[self.projeto.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=self.projeto.pk).exists())

    def test_administrador_ve_todos(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('projects:projetos')).context['paginator'].count, 2)


class PosseAnotacaoTests(Base):
    def setUp(self):
        super().setUp()
        self.nota = Note.objects.create(content='Privada', task=self.tarefa, author=self.dev)

    def test_form_valid_grava_o_autor(self):
        self.client.force_login(self.gerente)
        self.client.post(reverse('projects:anotacao_criar'), {'task': self.tarefa.pk, 'content': 'Minha'})
        self.assertEqual(Note.objects.get(content='Minha').author, self.gerente)

    def test_lista_somente_as_proprias(self):
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.get(reverse('projects:anotacoes')).context['paginator'].count, 0)

    def test_nao_autor_recebe_404_mesmo_administrador(self):
        for usuario in [self.gerente, self.admin]:
            self.client.force_login(usuario)
            for nome in ['anotacao_detalhe', 'anotacao_editar', 'anotacao_excluir']:
                with self.subTest(usuario=usuario.email, nome=nome):
                    self.assertEqual(self.client.get(reverse(f'projects:{nome}', args=[self.nota.pk])).status_code, 404)

    def test_detalhe_da_tarefa_nao_mostra_nota_alheia(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('projects:tarefa_detalhe', args=[self.tarefa.pk]))
        self.assertNotContains(response, 'Privada')

    def test_nao_anota_em_tarefa_de_projeto_alheio(self):
        self.client.force_login(self.estranho)
        response = self.client.post(reverse('projects:anotacao_criar'), {'task': self.tarefa.pk, 'content': 'X'})
        self.assertIn('task', response.context['form'].errors)


class PosseApontamentoTests(Base):
    def setUp(self):
        super().setUp()
        self.apontamento = TimeEntry.objects.create(task=self.tarefa, author=self.dev, hours='2.50', description='Privado')

    def dados(self, **extra):
        return {'task': self.tarefa.pk, 'date': '2026-11-10', 'hours': '1.50', **extra}

    def test_form_valid_grava_o_autor_mesmo_informando_outro(self):
        self.client.force_login(self.gerente)
        self.client.post(reverse('projects:apontamento_criar'), self.dados(description='Meu', author=self.dev.pk))
        self.assertEqual(TimeEntry.objects.get(description='Meu').author, self.gerente)

    def test_lista_somente_os_proprios_e_soma_as_horas(self):
        TimeEntry.objects.create(task=self.tarefa, author=self.gerente, hours='1.00')
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:apontamentos'))
        self.assertEqual(list(response.context['apontamentos']), [self.apontamento])
        self.assertEqual(response.context['total_horas'], Decimal('2.50'))

    def test_nao_autor_recebe_404_mesmo_administrador(self):
        for usuario in [self.gerente, self.admin]:
            self.client.force_login(usuario)
            for nome in ['apontamento_detalhe', 'apontamento_editar', 'apontamento_excluir']:
                with self.subTest(usuario=usuario.email, nome=nome):
                    self.assertEqual(self.client.get(reverse(f'projects:{nome}', args=[self.apontamento.pk])).status_code, 404)

    def test_nao_autor_nao_altera_nem_exclui_por_post(self):
        self.client.force_login(self.admin)
        editar = self.client.post(reverse('projects:apontamento_editar', args=[self.apontamento.pk]), self.dados())
        excluir = self.client.post(reverse('projects:apontamento_excluir', args=[self.apontamento.pk]))
        self.assertEqual((editar.status_code, excluir.status_code), (404, 404))
        self.apontamento.refresh_from_db()
        self.assertEqual(self.apontamento.hours, Decimal('2.50'))

    def test_autor_altera_e_exclui_com_mensagens(self):
        self.client.force_login(self.dev)
        response = self.client.post(reverse('projects:apontamento_editar', args=[self.apontamento.pk]), self.dados())
        self.assertIn('Apontamento alterado.', self.mensagens(response))
        self.apontamento.refresh_from_db()
        self.assertEqual(self.apontamento.hours, Decimal('1.50'))
        response = self.client.post(reverse('projects:apontamento_excluir', args=[self.apontamento.pk]))
        self.assertIn('Apontamento excluído.', self.mensagens(response))
        self.assertFalse(TimeEntry.objects.filter(pk=self.apontamento.pk).exists())

    def test_detalhe_da_tarefa_nao_mostra_apontamento_alheio(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('projects:tarefa_detalhe', args=[self.tarefa.pk]))
        self.assertNotContains(response, 'Privado')

    def test_nao_aponta_em_tarefa_de_projeto_alheio(self):
        self.client.force_login(self.estranho)
        response = self.client.post(reverse('projects:apontamento_criar'), self.dados())
        self.assertIn('task', response.context['form'].errors)

    def test_horas_fora_do_limite_sao_recusadas(self):
        self.client.force_login(self.dev)
        for horas in ['0', '24.25']:
            with self.subTest(horas):
                response = self.client.post(reverse('projects:apontamento_criar'), self.dados(hours=horas))
                self.assertIn('hours', response.context['form'].errors)

    def test_registros_privados_ficam_fora_do_django_admin(self):
        self.assertFalse(admin.site.is_registered(TimeEntry))
        self.assertFalse(admin.site.is_registered(Note))

    def test_anonimo_vai_ao_login(self):
        response = self.client.get(reverse('projects:apontamentos'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_telas_renderizam_para_o_autor(self):
        self.client.force_login(self.dev)
        args = [self.apontamento.pk]
        for nome, a in [('apontamentos', []), ('apontamento_criar', []), ('apontamento_detalhe', args), ('apontamento_editar', args), ('apontamento_excluir', args)]:
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(f'projects:{nome}', args=a)).status_code, 200)


class MovimentoTests(Base):
    def mover(self, stage):
        return self.client.post(reverse('projects:tarefa_mover', args=[self.tarefa.pk]), {'stage': stage})

    def test_participante_move_tarefa(self):
        self.client.force_login(self.dev)
        response = self.mover(self.estagios[1].pk)
        self.assertRedirects(response, reverse('projects:quadro', args=[self.projeto.pk]))
        self.tarefa.refresh_from_db()
        self.assertEqual(self.tarefa.stage, self.estagios[1])
        self.assertIn('Tarefa movida para Em andamento.', self.mensagens(response))

    def test_recusa_estagio_de_outro_projeto(self):
        self.client.force_login(self.dev)
        response = self.mover(self.outro_projeto.stages.first().pk)
        self.tarefa.refresh_from_db()
        self.assertEqual(self.tarefa.stage, self.estagios[0])
        self.assertIn('Escolha um estágio do mesmo projeto.', self.mensagens(response))

    def test_estagio_invalido_nao_quebra(self):
        self.client.force_login(self.dev)
        self.assertEqual(self.mover('abc').status_code, 302)

    def test_nao_participante_recebe_404(self):
        self.client.force_login(self.estranho)
        self.assertEqual(self.mover(self.estagios[1].pk).status_code, 404)

    def test_get_nao_e_permitido(self):
        self.client.force_login(self.dev)
        self.assertEqual(self.client.get(reverse('projects:tarefa_mover', args=[self.tarefa.pk])).status_code, 405)

    def test_quadro_exibe_colunas(self):
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:quadro', args=[self.projeto.pk]))
        self.assertEqual(len(response.context['colunas']), 4)
        self.assertContains(response, 'Login')

    def test_quadro_de_nao_participante_e_404(self):
        self.client.force_login(self.estranho)
        self.assertEqual(self.client.get(reverse('projects:quadro', args=[self.projeto.pk])).status_code, 404)


class FiltrosTests(Base):
    def test_filtra_tarefas_por_titulo_e_prioridade(self):
        Task.objects.create(title='Relatório', stage=self.estagios[0], priority='urgent')
        Task.objects.create(title='Relatório antigo', stage=self.estagios[0], priority='low')
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:tarefas'), {'title': 'relat', 'priority': 'urgent'})
        self.assertEqual([t.title for t in response.context['tarefas']], ['Relatório'])

    def test_filtra_projetos_por_nome_e_equipe(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('projects:projetos'), {'name': 'por', 'team': self.equipe.pk})
        self.assertEqual(list(response.context['projetos']), [self.projeto])

    def test_filtro_nao_revela_registros_de_outros(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('projects:projetos'), {'name': 'ERP'})
        self.assertEqual(list(response.context['projetos']), [])

    def test_opcoes_do_filtro_respeitam_o_usuario(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('projects:projetos'))
        self.assertEqual(list(response.context['filter'].form.fields['team'].queryset), [self.equipe])

    def test_equipe_alheia_no_filtro_nao_retorna_registros(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('projects:projetos'), {'team': self.outra_equipe.pk})
        self.assertEqual(list(response.context['projetos']), [])

    def test_paginacao_preserva_a_busca(self):
        for i in range(12):
            Task.objects.create(title=f'Item {i}', stage=self.estagios[0], priority='high')
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:tarefas'), {'title': 'Item', 'priority': 'high'})
        self.assertContains(response, 'title=Item&amp;priority=high&amp;page=2')
        pagina2 = self.client.get(reverse('projects:tarefas'), {'title': 'Item', 'priority': 'high', 'page': 2})
        self.assertEqual(len(pagina2.context['tarefas']), 2)
        self.assertContains(pagina2, 'title=Item&amp;priority=high&amp;page=1')

    def test_templatetag_substitui_a_pagina_atual(self):
        request = RequestFactory().get('/', {'title': 'a b', 'page': '3'})
        self.assertEqual(url_pagina({'request': request}, 4), '?title=a+b&page=4')


class QueriesTests(Base):
    """A quantidade de queries das telas não pode crescer com o número de registros."""

    def contar(self, url):
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.client.get(url).status_code, 200)
        return len(queries)

    def criar_registros(self, quantidade):
        for i in range(quantidade):
            usuario = criar_usuario(f'membro{Task.objects.count()}@exemplo.com', DESENVOLVEDOR)
            self.equipe.members.add(usuario)
            self.projeto.assigned_members.add(usuario)
            tarefa = Task.objects.create(title=f'T{i}', stage=self.estagios[i % 4], assigned_to=usuario)
            Note.objects.create(content='n', task=tarefa, author=self.gerente)
            TimeEntry.objects.create(task=tarefa, author=self.gerente, hours='1.00')
            projeto = self.criar_projeto(f'P{Project.objects.count()}', self.equipe, self.gerente)
            projeto.assigned_members.add(usuario)

    def test_listas_e_quadro_nao_tem_n_mais_1(self):
        self.client.force_login(self.gerente)
        urls = [
            reverse(f'projects:{nome}') for nome in ['tarefas', 'projetos', 'estagios', 'equipes', 'anotacoes', 'apontamentos', 'quadros']
        ] + [reverse('projects:quadro', args=[self.projeto.pk]), reverse('pages:home')]
        self.criar_registros(2)
        antes = {url: self.contar(url) for url in urls}
        self.criar_registros(6)
        depois = {url: self.contar(url) for url in urls}
        self.assertEqual(antes, depois)


class MensagensECrudTests(Base):
    def test_ciclo_completo_de_tarefa_com_mensagens(self):
        self.client.force_login(self.dev)
        response = self.client.post(reverse('projects:tarefa_criar'), {'title': 'Nova', 'stage': self.estagios[0].pk, 'priority': 'high'})
        self.assertIn('Tarefa cadastrada.', self.mensagens(response))
        tarefa = Task.objects.get(title='Nova')
        response = self.client.post(reverse('projects:tarefa_editar', args=[tarefa.pk]), {'title': 'Editada', 'stage': self.estagios[0].pk, 'priority': 'low'})
        self.assertIn('Tarefa alterada.', self.mensagens(response))
        response = self.client.post(reverse('projects:tarefa_excluir', args=[tarefa.pk]))
        self.assertIn('Tarefa excluída.', self.mensagens(response))
        self.assertFalse(Task.objects.filter(pk=tarefa.pk).exists())

    def test_telas_renderizam_para_o_administrador(self):
        Note.objects.create(content='N', task=self.tarefa, author=self.admin)
        self.client.force_login(self.admin)
        nota = Note.objects.get(content='N')
        rotas = [
            ('equipes', []), ('equipe_criar', []), ('equipe_detalhe', [self.equipe.pk]), ('equipe_editar', [self.equipe.pk]), ('equipe_excluir', [self.equipe.pk]),
            ('projetos', []), ('projeto_criar', []), ('projeto_detalhe', [self.projeto.pk]), ('projeto_editar', [self.projeto.pk]), ('projeto_excluir', [self.projeto.pk]),
            ('estagios', []), ('estagio_criar', []), ('estagio_detalhe', [self.estagios[0].pk]), ('estagio_editar', [self.estagios[0].pk]), ('estagio_excluir', [self.estagios[0].pk]),
            ('tarefas', []), ('tarefa_criar', []), ('tarefa_detalhe', [self.tarefa.pk]), ('tarefa_editar', [self.tarefa.pk]), ('tarefa_excluir', [self.tarefa.pk]),
            ('anotacoes', []), ('anotacao_criar', []), ('anotacao_detalhe', [nota.pk]), ('anotacao_editar', [nota.pk]), ('anotacao_excluir', [nota.pk]),
            ('quadros', []), ('quadro', [self.projeto.pk]),
        ]
        for nome, args in rotas:
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(f'projects:{nome}', args=args)).status_code, 200)

    def test_listas_sao_paginadas(self):
        for i in range(12):
            Task.objects.create(title=f'T{i}', stage=self.estagios[0])
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:tarefas'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['tarefas']), 10)


class NavegacaoTests(Base):
    """Fluxo de navegação: retorno à origem, pré-seleção, ações no detalhe e estados vazios."""

    def setUp(self):
        super().setUp()
        self.url_tarefa = reverse('projects:tarefa_detalhe', args=[self.tarefa.pk])
        self.url_quadro = reverse('projects:quadro', args=[self.projeto.pk])

    def test_salvar_volta_para_a_origem(self):
        self.client.force_login(self.dev)
        url = f"{reverse('projects:anotacao_criar')}?tarefa={self.tarefa.pk}&next={self.url_tarefa}"
        response = self.client.post(url, {'task': self.tarefa.pk, 'content': 'Lembrar do CSRF'})
        self.assertRedirects(response, self.url_tarefa)

    def test_next_externo_e_ignorado(self):
        self.client.force_login(self.dev)
        url = f"{reverse('projects:anotacao_criar')}?next=https://evil.test/roubo"
        response = self.client.post(url, {'task': self.tarefa.pk, 'content': 'Teste'})
        self.assertRedirects(response, reverse('projects:anotacoes'))
        response = self.client.get(url)
        self.assertEqual(response.context['voltar'], reverse('projects:anotacoes'))

    def test_cancelar_usa_a_origem(self):
        self.client.force_login(self.dev)
        response = self.client.get(f"{reverse('projects:tarefa_editar', args=[self.tarefa.pk])}?next={self.url_tarefa}")
        self.assertEqual(response.context['voltar'], self.url_tarefa)
        self.assertContains(response, f'href="{self.url_tarefa}"')

    def test_excluir_tarefa_pelo_detalhe_volta_ao_quadro(self):
        self.client.force_login(self.dev)
        response = self.client.get(self.url_tarefa)
        url_excluir = f"{reverse('projects:tarefa_excluir', args=[self.tarefa.pk])}?next={self.url_quadro}"
        self.assertContains(response, url_excluir)
        response = self.client.post(f"{reverse('projects:tarefa_excluir', args=[self.tarefa.pk])}?next={self.url_quadro}")
        self.assertRedirects(response, self.url_quadro)
        self.assertFalse(Task.objects.filter(pk=self.tarefa.pk).exists())

    def test_estagio_pre_selecionado_pelo_quadro(self):
        self.client.force_login(self.dev)
        response = self.client.get(f"{reverse('projects:tarefa_criar')}?estagio={self.estagios[1].pk}")
        self.assertEqual(response.context['form'].initial.get('stage'), self.estagios[1].pk)

    def test_estagio_de_projeto_alheio_nao_e_pre_selecionado(self):
        self.client.force_login(self.dev)
        alheio = self.outro_projeto.stages.first()
        response = self.client.get(f"{reverse('projects:tarefa_criar')}?estagio={alheio.pk}")
        self.assertNotIn('stage', response.context['form'].initial)

    def test_quadro_tem_atalhos_de_nova_tarefa(self):
        self.client.force_login(self.dev)
        response = self.client.get(self.url_quadro)
        for estagio in self.estagios:
            self.assertContains(response, f"?estagio={estagio.pk}&amp;next=")

    def test_excluir_equipe_no_detalhe_so_para_administrador(self):
        url_excluir = reverse('projects:equipe_excluir', args=[self.equipe.pk])
        self.client.force_login(self.gerente)
        self.assertNotContains(self.client.get(reverse('projects:equipe_detalhe', args=[self.equipe.pk])), url_excluir)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('projects:equipe_detalhe', args=[self.equipe.pk])), url_excluir)

    def test_detalhes_oferecem_excluir(self):
        nota = Note.objects.create(content='N', task=self.tarefa, author=self.gerente)
        apontamento = TimeEntry.objects.create(task=self.tarefa, author=self.gerente, hours='1.00')
        self.client.force_login(self.gerente)
        casos = [
            ('projeto', self.projeto.pk), ('estagio', self.estagios[0].pk), ('tarefa', self.tarefa.pk),
            ('anotacao', nota.pk), ('apontamento', apontamento.pk),
        ]
        for nome, pk in casos:
            with self.subTest(nome):
                response = self.client.get(reverse(f'projects:{nome}_detalhe', args=[pk]))
                self.assertContains(response, reverse(f'projects:{nome}_excluir', args=[pk]))
                self.assertContains(response, 'data-excluir')

    def test_quadro_sem_tarefas_orienta_o_usuario(self):
        self.tarefa.delete()
        self.client.force_login(self.dev)
        response = self.client.get(self.url_quadro)
        self.assertContains(response, 'Este projeto ainda não tem tarefas')
        self.assertContains(response, '<p class="board-empty">Nenhuma tarefa</p>', count=4)

    def test_coluna_vazia_mostra_aviso(self):
        self.client.force_login(self.dev)
        response = self.client.get(self.url_quadro)
        self.assertNotContains(response, 'Este projeto ainda não tem tarefas')
        self.assertContains(response, '<p class="board-empty">Nenhuma tarefa</p>', count=3)

    def test_home_sugere_proximo_passo_por_papel(self):
        novo_gerente = criar_usuario('novo@exemplo.com', GERENTE)
        self.client.force_login(novo_gerente)
        self.assertContains(self.client.get(reverse('pages:home')), reverse('projects:projeto_criar'))
        self.client.force_login(self.estranho)
        response = self.client.get(reverse('pages:home'))
        self.assertNotContains(response, reverse('projects:projeto_criar'))
        self.assertContains(response, 'Peça ao gerente')
        self.assertContains(response, reverse('projects:quadros'))


class PaginasDeErroTests(TestCase):
    def test_erro_500_usa_o_template_do_projeto(self):
        response = server_error(RequestFactory().get('/'))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Algo deu errado', response.content.decode())

    def test_erro_400_usa_o_template_do_projeto(self):
        response = bad_request(RequestFactory().get('/'), exception=None)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Requisição inválida', response.content.decode())

