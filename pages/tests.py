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
