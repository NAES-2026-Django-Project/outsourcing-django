from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from django_filters.views import FilterView

from accounts.mixins import SomenteAdministradorMixin
from accounts.models import User

from .filters import ChamadaIAFilter
from .forms import ConfiguracaoIAForm, CotaUsuarioForm
from .markdown import markdown_seguro
from .models import ChamadaIA, ConfiguracaoIA, CotaUsuario, MensagemAssistente
from .services import (
    CotaExcedida, ErroIA, consumo_mensal, inicio_do_mes, limite_mensal, perguntar_ao_assistente, testar_conexao,
)

TAMANHO_MAXIMO_PERGUNTA = 2000


def resumo_de_consumo(usuario):
    consumo = consumo_mensal(usuario)
    limite = limite_mensal(usuario)
    percentual = min(100, round(consumo * 100 / limite)) if limite else 100
    return {'consumo': consumo, 'limite': limite, 'percentual': percentual}


# Assistente

class AssistenteView(LoginRequiredMixin, TemplateView):
    template_name = 'ia/assistente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ultimas = MensagemAssistente.objects.filter(usuario=self.request.user).order_by('-criado_em', '-id')[:50]
        context['mensagens'] = list(reversed(ultimas))
        context.update(resumo_de_consumo(self.request.user))
        return context


class PerguntarView(LoginRequiredMixin, View):
    """Recebe a pergunta por AJAX (protegida pelo CSRF do Django) e devolve a resposta em HTML sanitizado."""

    http_method_names = ['post']

    def post(self, request):
        pergunta = request.POST.get('pergunta', '').strip()
        if not pergunta:
            return JsonResponse({'erro': 'Escreva uma pergunta.'}, status=400)
        if len(pergunta) > TAMANHO_MAXIMO_PERGUNTA:
            return JsonResponse({'erro': f'A pergunta pode ter até {TAMANHO_MAXIMO_PERGUNTA} caracteres.'}, status=400)
        try:
            resposta = perguntar_ao_assistente(request.user, pergunta)
        except CotaExcedida as erro:
            return JsonResponse({'erro': str(erro), **resumo_de_consumo(request.user)}, status=429)
        except ErroIA as erro:
            return JsonResponse({'erro': str(erro)}, status=503)
        return JsonResponse({'resposta_html': markdown_seguro(resposta), **resumo_de_consumo(request.user)})


class LimparHistoricoView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request):
        MensagemAssistente.objects.filter(usuario=request.user).delete()
        messages.success(request, 'Histórico do assistente apagado.')
        return redirect('ia:assistente')


class MeuConsumoView(LoginRequiredMixin, ListView):
    template_name = 'ia/meu_consumo.html'
    context_object_name = 'chamadas'
    paginate_by = 10

    def get_queryset(self):
        return ChamadaIA.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(resumo_de_consumo(self.request.user))
        context['inicio_do_mes'] = inicio_do_mes()
        return context


# Administração

class ConfiguracaoView(SomenteAdministradorMixin, SuccessMessageMixin, UpdateView):
    form_class = ConfiguracaoIAForm
    template_name = 'ia/configuracao.html'
    success_url = reverse_lazy('ia:configuracao')
    success_message = 'Configuração da IA salva.'
    context_object_name = 'config'

    def get_object(self, queryset=None):
        return ConfiguracaoIA.carregar()


class TestarConexaoView(SomenteAdministradorMixin, View):
    http_method_names = ['post']

    def post(self, request):
        sucesso, mensagem = testar_conexao(request.user)
        (messages.success if sucesso else messages.error)(request, mensagem)
        return redirect('ia:configuracao')


class RequisicaoListView(SomenteAdministradorMixin, FilterView):
    filterset_class = ChamadaIAFilter
    template_name = 'ia/requisicao_list.html'
    context_object_name = 'chamadas'
    paginate_by = 20

    def get_queryset(self):
        return ChamadaIA.objects.select_related('usuario')


class RequisicaoDetailView(SomenteAdministradorMixin, DetailView):
    template_name = 'ia/requisicao_detail.html'
    context_object_name = 'chamada'

    def get_queryset(self):
        return ChamadaIA.objects.select_related('usuario')


class UsoPorUsuarioView(SomenteAdministradorMixin, ListView):
    template_name = 'ia/uso_por_usuario.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        no_mes = Q(chamadas_ia__criado_em__gte=inicio_do_mes())
        return User.objects.select_related('cota_ia').annotate(
            tokens_mes=Coalesce(Sum(F('chamadas_ia__tokens_entrada') + F('chamadas_ia__tokens_saida'), filter=no_mes), 0),
            chamadas_mes=Count('chamadas_ia', filter=no_mes),
        ).order_by('-tokens_mes', 'first_name', 'last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        padrao = ConfiguracaoIA.carregar().cota_mensal_padrao
        for usuario in context['usuarios']:
            cota = getattr(usuario, 'cota_ia', None)
            usuario.limite = cota.limite_mensal if cota and cota.limite_mensal is not None else padrao
            usuario.cota_propria = bool(cota and cota.limite_mensal is not None)
        context['cota_padrao'] = padrao
        return context


class CotaUsuarioView(SomenteAdministradorMixin, SuccessMessageMixin, UpdateView):
    form_class = CotaUsuarioForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('ia:uso_por_usuario')
    success_message = 'Cota do usuário atualizada.'
    context_object_name = 'cota'

    def get_object(self, queryset=None):
        usuario = get_object_or_404(User, pk=self.kwargs['pk'])
        return CotaUsuario.objects.get_or_create(usuario=usuario)[0]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Cota de IA de {self.object.usuario}', 'botao': 'Salvar', 'voltar': self.success_url})
        return context
