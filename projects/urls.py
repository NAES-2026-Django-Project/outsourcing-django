from django.urls import path

from . import views

app_name = 'projects'


def crud(prefixo, nome_lista, nome, lista, detalhe, criar, editar, excluir):
    return [
        path(f'{prefixo}/', lista.as_view(), name=nome_lista),
        path(f'{prefixo}/novo/', criar.as_view(), name=f'{nome}_criar'),
        path(f'{prefixo}/<int:pk>/', detalhe.as_view(), name=f'{nome}_detalhe'),
        path(f'{prefixo}/<int:pk>/editar/', editar.as_view(), name=f'{nome}_editar'),
        path(f'{prefixo}/<int:pk>/excluir/', excluir.as_view(), name=f'{nome}_excluir'),
    ]


urlpatterns = [
    *crud('equipes', 'equipes', 'equipe', views.TeamListView, views.TeamDetailView,
          views.TeamCreateView, views.TeamUpdateView, views.TeamDeleteView),
    *crud('projetos', 'projetos', 'projeto', views.ProjectListView, views.ProjectDetailView,
          views.ProjectCreateView, views.ProjectUpdateView, views.ProjectDeleteView),
    *crud('estagios', 'estagios', 'estagio', views.StageListView, views.StageDetailView,
          views.StageCreateView, views.StageUpdateView, views.StageDeleteView),
    *crud('tarefas', 'tarefas', 'tarefa', views.TaskListView, views.TaskDetailView,
          views.TaskCreateView, views.TaskUpdateView, views.TaskDeleteView),
    *crud('anotacoes', 'anotacoes', 'anotacao', views.NoteListView, views.NoteDetailView,
          views.NoteCreateView, views.NoteUpdateView, views.NoteDeleteView),
]
