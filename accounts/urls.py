from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('entrar/', LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('senha/', views.TrocarSenhaView.as_view(), name='senha'),
    path('conta/', views.ContaView.as_view(), name='conta'),
    path('conta/dados/', views.DadosPessoaisView.as_view(), name='dados'),
    path('conta/perfil/', views.PerfilView.as_view(), name='perfil'),
    path('conta/endereco/', views.EnderecoView.as_view(), name='endereco'),
    path('usuarios/', views.UsuarioListView.as_view(), name='usuarios'),
    path('usuarios/<int:pk>/papel/', views.UsuarioPapelView.as_view(), name='usuario_papel'),
]
