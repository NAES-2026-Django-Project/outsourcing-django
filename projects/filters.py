import django_filters

from accounts.models import User

from .forms import DateInput
from .models import Priority, Project, Task, Team


def equipes_do_usuario(request):
    return Team.objects.visiveis_para(request.user)


def projetos_do_usuario(request):
    return Project.objects.com_participacao(request.user)


def responsaveis_visiveis(request):
    return User.objects.filter(my_tasks__in=Task.objects.visiveis_para(request.user)).distinct()


class ProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label='Nome', lookup_expr='icontains')
    team = django_filters.ModelChoiceFilter(label='Equipe', queryset=equipes_do_usuario, empty_label='Todas')
    inicio = django_filters.DateFilter(
        label='Início a partir de', field_name='start_date', lookup_expr='gte', widget=DateInput(),
    )

    class Meta:
        model = Project
        fields = ['name', 'team', 'inicio']


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label='Título', lookup_expr='icontains')
    projeto = django_filters.ModelChoiceFilter(
        label='Projeto', field_name='stage__project', queryset=projetos_do_usuario, empty_label='Todos',
    )
    priority = django_filters.ChoiceFilter(label='Prioridade', choices=Priority.choices, empty_label='Todas')
    assigned_to = django_filters.ModelChoiceFilter(
        label='Responsável', queryset=responsaveis_visiveis, empty_label='Todos',
    )
    prazo = django_filters.DateFilter(
        label='Prazo até', field_name='due_date', lookup_expr='lte', widget=DateInput(),
    )

    class Meta:
        model = Task
        fields = ['title', 'projeto', 'priority', 'assigned_to', 'prazo']
