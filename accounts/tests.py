from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE, GRUPOS
from .models import User


def criar_usuario(email, grupo=None):
    user = User.objects.create_user(email=email, password='senha-teste-123', first_name='Nome', last_name='Teste')
    if grupo:
        user.groups.add(Group.objects.get(name=grupo))
    return user


class GruposTests(TestCase):
    def test_migration_cria_os_tres_grupos(self):
        self.assertEqual(set(Group.objects.values_list('name', flat=True)), set(GRUPOS))


class CadastroTests(TestCase):
    dados = {
        'email': 'Nova@Exemplo.com', 'first_name': 'Nova', 'last_name': 'Pessoa', 'phone': '',
        'password1': 'senha-forte-987', 'password2': 'senha-forte-987',
    }

    def test_cadastro_entra_como_desenvolvedor_mesmo_tentando_outro_grupo(self):
        dados = {**self.dados, 'groups': [Group.objects.get(name=ADMINISTRADOR).pk], 'papel': ADMINISTRADOR, 'is_superuser': 'on'}
        response = self.client.post(reverse('accounts:cadastro'), dados)
        self.assertRedirects(response, reverse('accounts:login'))
        user = User.objects.get(email='nova@exemplo.com')
        self.assertEqual(set(user.groups.values_list('name', flat=True)), {DESENVOLVEDOR})
        self.assertFalse(user.is_superuser)

    def test_cadastro_cria_perfil_e_endereco(self):
        self.client.post(reverse('accounts:cadastro'), self.dados)
        user = User.objects.get(email='nova@exemplo.com')
        self.assertIsNotNone(user.profile.pk)
        self.assertIsNotNone(user.address.pk)

    def test_email_duplicado_sem_diferenciar_maiusculas(self):
        criar_usuario('nova@exemplo.com')
        response = self.client.post(reverse('accounts:cadastro'), self.dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)


class AutenticacaoTests(TestCase):
    def setUp(self):
        self.user = criar_usuario('dev@exemplo.com', DESENVOLVEDOR)

    def test_login_e_logout(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'dev@exemplo.com', 'password': 'senha-teste-123'})
        self.assertRedirects(response, reverse('pages:home'))
        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('pages:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_troca_de_senha(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:senha'), {
            'old_password': 'senha-teste-123', 'new_password1': 'outra-senha-456', 'new_password2': 'outra-senha-456',
        }, follow=True)
        self.assertContains(response, 'Senha alterada.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('outra-senha-456'))

    def test_conta_exige_login(self):
        response = self.client.get(reverse('accounts:conta'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)


class GestaoUsuariosTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario('admin@exemplo.com', ADMINISTRADOR)
        self.dev = criar_usuario('dev@exemplo.com', DESENVOLVEDOR)

    def test_anonimo_vai_ao_login(self):
        response = self.client.get(reverse('accounts:usuarios'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_grupo_errado_recebe_403(self):
        self.client.force_login(self.dev)
        self.assertEqual(self.client.get(reverse('accounts:usuarios')).status_code, 403)

    def test_administrador_altera_papel(self):
        self.client.force_login(self.admin)
        url = reverse('accounts:usuario_papel', args=[self.dev.pk])
        response = self.client.post(url, {'papel': GERENTE, 'is_active': 'on'})
        self.assertRedirects(response, reverse('accounts:usuarios'))
        self.assertEqual(set(self.dev.groups.values_list('name', flat=True)), {GERENTE})

    def test_menu_mantem_usuario_logado_ao_editar_outro_usuario(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('accounts:usuario_papel', args=[self.dev.pk]))
        self.assertEqual(response.context['request'].user, self.admin)
        self.assertContains(response, reverse('accounts:usuarios'))
