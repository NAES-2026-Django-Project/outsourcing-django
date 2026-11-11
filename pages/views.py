from django.views.generic import TemplateView

from projects.models import Project, Task


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            tarefas = Task.objects.visiveis_para(user).select_related('stage__project')
            abertas = tarefas.filter(stage__stage_type__in=['backlog', 'doing'])
            projetos = Project.objects.com_participacao(user).select_related('team')
            context.update({
                'total_abertas': abertas.count(),
                'total_urgentes': abertas.filter(priority='urgent').count(),
                'total_projetos': projetos.count(),
                'tarefas_recentes': tarefas.order_by('-created_at')[:5],
                'projetos_recentes': projetos.order_by('-created_at')[:5],
            })
        return context


class SobreView(TemplateView):
    template_name = 'pages/sobre.html'
    extra_context = {'titulo': 'Sobre o projeto'}
