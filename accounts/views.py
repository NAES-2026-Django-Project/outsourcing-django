from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import CadastroForm, DadosPessoaisForm, PapelUsuarioForm
from .mixins import SomenteAdministradorMixin
from .models import Address, Profile, User


class CadastroView(SuccessMessageMixin, CreateView):
    form_class = CadastroForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:login')
    success_message = 'Conta criada. Entre com seu e-mail e senha.'
    extra_context = {'titulo': 'Criar conta', 'botao': 'Criar conta'}


class TrocarSenhaView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:conta')
    success_message = 'Senha alterada.'
    extra_context = {'titulo': 'Alterar senha', 'voltar': reverse_lazy('accounts:conta'), 'botao': 'Alterar senha'}


class ContaView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/conta.html'


class EditarContaBase(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edita sempre um registro do próprio usuário logado."""

    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:conta')


class DadosPessoaisView(EditarContaBase):
    form_class = DadosPessoaisForm
    context_object_name = 'usuario'
    success_message = 'Dados pessoais atualizados.'
    extra_context = {'titulo': 'Dados pessoais', 'voltar': reverse_lazy('accounts:conta'), 'botao': 'Salvar'}

    def get_object(self, queryset=None):
        return self.request.user


class PerfilView(EditarContaBase):
    model = Profile
    fields = ['instagram_url', 'facebook_url', 'linkedin_url', 'twitter_url']
    success_message = 'Perfil atualizado.'
    extra_context = {'titulo': 'Perfil', 'voltar': reverse_lazy('accounts:conta'), 'botao': 'Salvar'}

    def get_object(self, queryset=None):
        return self.request.user.profile


class EnderecoView(EditarContaBase):
    model = Address
    fields = ['country', 'state', 'city', 'cep']
    success_message = 'Endereço atualizado.'
    extra_context = {'titulo': 'Endereço', 'voltar': reverse_lazy('accounts:conta'), 'botao': 'Salvar'}

    def get_object(self, queryset=None):
        return self.request.user.address


class UsuarioListView(SomenteAdministradorMixin, ListView):
    model = User
    template_name = 'accounts/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.prefetch_related('groups')


class UsuarioPapelView(SomenteAdministradorMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = PapelUsuarioForm
    context_object_name = 'usuario'
    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:usuarios')
    success_message = 'Usuário atualizado.'
    extra_context = {'titulo': 'Papel do usuário', 'voltar': reverse_lazy('accounts:usuarios'), 'botao': 'Salvar'}
