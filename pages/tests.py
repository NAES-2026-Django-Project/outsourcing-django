from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.constants import GERENTE
from accounts.tests import criar_usuario
from projects.models import Project, Task, Team


class PaginasTests(TestCase):
    def test_sobre_e_publica_e_exibe_os_diagramas(self):
        response = self.client.get(reverse('pages:sobre'))
        self.assertContains(response, 'img/diagrama-casos-de-uso.png')
        self.assertContains(response, 'img/diagrama-classes.png')
        self.assertEqual(response.context['titulo'], 'Sobre o projeto')

    def test_layout_carrega_jquery_e_plugins(self):
        response = self.client.get(reverse('pages:sobre'))
        for script in ['jquery.min.js', 'bootbox.all.min.js', 'jquery.mask.min.js', 'select2.min.js', 'js/app.js']:
            with self.subTest(script):
                self.assertContains(response, script)

    def test_menu_de_visitante(self):
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, 'Criar conta')
        self.assertNotContains(response, reverse('projects:tarefas'))

    def test_home_logada_lista_recentes(self):
        gerente = criar_usuario('g@exemplo.com', GERENTE)
        equipe = Team.objects.create(name='Atlas', manager=gerente)
        projeto = Project.objects.create(name='Portal', team=equipe, created_by=gerente, start_date=date(2026, 11, 1))
        Task.objects.create(title='Urgente', stage=projeto.stages.first(), priority='urgent')
        self.client.force_login(gerente)
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.context['total_urgentes'], 1)
        self.assertContains(response, 'Urgente')
        self.assertContains(response, reverse('projects:tarefas'))


class InterfaceTests(TestCase):
    """Nova interface (DESIGN.md): componentes, layout e telas responsivas."""

    def setUp(self):
        from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR
        from projects.models import StageType

        self.admin = criar_usuario('admin@exemplo.com', ADMINISTRADOR)
        self.gerente = criar_usuario('gerente@exemplo.com', GERENTE)
        self.dev = criar_usuario('dev@exemplo.com', DESENVOLVEDOR)
        self.equipe = Team.objects.create(name='Atlas', manager=self.gerente)
        self.projeto = Project.objects.create(name='Portal', team=self.equipe, created_by=self.gerente, start_date=date(2026, 11, 1))
        self.projeto.assigned_members.add(self.dev)
        self.estagios = {s.stage_type: s for s in self.projeto.stages.all()}
        self.feita = Task.objects.create(title='Feita', stage=self.estagios[StageType.DONE], due_date=date(2020, 1, 1))
        self.aberta = Task.objects.create(title='Aberta', stage=self.estagios[StageType.BACKLOG], due_date=date(2020, 1, 1), priority='urgent')
        Task.objects.create(title='Futura', stage=self.estagios[StageType.DOING], due_date=date(2999, 1, 1))
        Task.objects.create(title='Aprovada', stage=self.estagios[StageType.APPROVED])

    def renderizar(self, codigo, **contexto):
        from django.template import Context, Template

        return Template('{% load ui %}' + codigo).render(Context(contexto))

    def test_etiquetas_seguem_o_mapeamento_do_design(self):
        casos = [
            ('{% etiqueta_prioridade t %}', {'t': self.aberta}, 'tag-error', 'Urgente'),
            ('{% etiqueta_estagio s %}', {'s': self.feita.stage}, 'tag-success', 'Concluído'),
            ('{% etiqueta_estagio s %}', {'s': self.aberta.stage}, 'tag-gray', 'Backlog'),
            ('{% etiqueta_papel u %}', {'u': self.admin}, 'tag-brand', 'Administrador'),
            ('{% etiqueta_papel u %}', {'u': self.gerente}, 'tag-info', 'Gerente'),
            ('{% etiqueta_grupo "Desenvolvedor" %}', {}, 'tag-gray', 'Desenvolvedor'),
        ]
        for codigo, contexto, classe, texto in casos:
            with self.subTest(codigo=codigo, texto=texto):
                html = self.renderizar(codigo, **contexto)
                self.assertIn(classe, html)
                self.assertIn(texto, html)

    def test_icone_iniciais_e_trilha(self):
        self.assertInHTML('<i class="bi bi-kanban " aria-hidden="true"></i>', self.renderizar('{% icone "kanban" %}'))
        self.assertEqual(self.renderizar('{{ u|iniciais }}', u=self.dev), 'NT')
        trilha = self.renderizar("{% trilha 'projects:tarefas' 'Tarefas' atual='Login' %}")
        self.assertIn('<a href="/tarefas/">Tarefas</a>', trilha)
        self.assertIn('<span>Login</span>', trilha)
        self.assertNotIn('&lt;a', trilha)

    def test_prazo_vencido_so_para_tarefa_aberta(self):
        self.assertTrue(self.aberta.vencida)
        self.assertFalse(self.feita.vencida)
        self.assertFalse(Task.objects.get(title='Futura').vencida)
        self.assertFalse(Task.objects.get(title='Aprovada').vencida)
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:quadro', args=[self.projeto.pk]))
        self.assertContains(response, 'prazo vencido', count=1)

    def test_painel_mostra_o_progresso_do_projeto(self):
        self.client.force_login(self.dev)
        response = self.client.get(reverse('pages:home'))
        projeto = response.context['projetos_recentes'][0]
        self.assertEqual((projeto.total_tarefas, projeto.tarefas_feitas), (4, 2))
        self.assertContains(response, 'aria-valuenow="50"')

    def test_layout_carrega_fonte_icones_tema_e_atalho(self):
        response = self.client.get(reverse('pages:sobre'))
        self.assertContains(response, "tema === 'dark' ? 'dark' : 'light'")  # claro é o padrão
        for trecho in ['family=Outfit', 'bootstrap-icons@1.11.3', 'id="alternar-tema"', 'id="alternar-menu"', 'href="#conteudo"']:
            with self.subTest(trecho):
                self.assertContains(response, trecho)

    def test_listas_viram_cartoes_no_celular(self):
        from ia.models import ChamadaIA
        from projects.models import Note, TimeEntry

        Note.objects.create(content='N', task=self.aberta, author=self.admin)
        TimeEntry.objects.create(task=self.aberta, author=self.admin, hours='1.00')
        ChamadaIA.objects.create(usuario=self.admin, origem='assistente', modelo='m', pergunta='P', status='sucesso')
        self.client.force_login(self.admin)
        rotas = [
            'projects:tarefas', 'projects:projetos', 'projects:estagios', 'projects:equipes', 'projects:anotacoes',
            'projects:apontamentos', 'projects:quadros', 'accounts:usuarios', 'ia:requisicoes', 'ia:uso_por_usuario', 'ia:meu_consumo',
        ]
        for rota in rotas:
            with self.subTest(rota):
                response = self.client.get(reverse(rota))
                self.assertContains(response, 'table-cards')
                self.assertContains(response, 'data-label=')

    def test_paginacao_numerada_preserva_os_filtros(self):
        for i in range(25):
            Task.objects.create(title=f'Item {i}', stage=self.estagios['backlog'], priority='high')
        self.client.force_login(self.dev)
        response = self.client.get(reverse('projects:tarefas'), {'title': 'Item', 'priority': 'high', 'page': 2})
        self.assertContains(response, 'Mostrando 11–20 de 25')
        self.assertContains(response, 'href="?title=Item&amp;priority=high&amp;page=3"')
        self.assertContains(response, '<span class="atual" aria-current="page">2</span>', html=True)

    def test_entrar_e_criar_conta_usam_o_layout_dividido(self):
        for rota in ['accounts:login', 'accounts:cadastro']:
            with self.subTest(rota):
                response = self.client.get(reverse(rota))
                self.assertContains(response, 'class="auth-side"')
                self.assertNotContains(response, 'id="sidebar"')
