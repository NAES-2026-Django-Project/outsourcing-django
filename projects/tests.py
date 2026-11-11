from datetime import date

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE
from accounts.tests import criar_usuario

from .models import Note, Project, Stage, Task, Team


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
