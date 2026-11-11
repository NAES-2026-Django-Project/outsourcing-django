from django.urls import path

from . import views

app_name = 'ia'

urlpatterns = [
    path('assistente/', views.AssistenteView.as_view(), name='assistente'),
    path('assistente/perguntar/', views.PerguntarView.as_view(), name='perguntar'),
    path('assistente/limpar/', views.LimparHistoricoView.as_view(), name='limpar'),
    path('ia/consumo/', views.MeuConsumoView.as_view(), name='meu_consumo'),
    path('ia/configuracao/', views.ConfiguracaoView.as_view(), name='configuracao'),
    path('ia/configuracao/testar/', views.TestarConexaoView.as_view(), name='testar'),
    path('ia/requisicoes/', views.RequisicaoListView.as_view(), name='requisicoes'),
    path('ia/requisicoes/<int:pk>/', views.RequisicaoDetailView.as_view(), name='requisicao_detalhe'),
    path('ia/usuarios/', views.UsoPorUsuarioView.as_view(), name='uso_por_usuario'),
    path('ia/usuarios/<int:pk>/cota/', views.CotaUsuarioView.as_view(), name='cota_usuario'),
]
