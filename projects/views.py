from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_filters.views import FilterView

from accounts.mixins import AdministradorOuGerenteMixin, SomenteAdministradorMixin

from .filters import ProjectFilter, TaskFilter
from .forms import NoteForm, ProjectForm, StageForm, TaskForm, TeamForm, TimeEntryForm
from .models import Note, Project, Stage, Task, Team, TimeEntry

ITENS_POR_PAGINA = 10


class FormComUsuarioMixin:
    """Entrega o usuário logado ao formulário, para restringir as opções."""

    template_name = 'crud/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RetornoMixin:
    """Volta à tela de origem (`?next=`) ao salvar, excluir ou cancelar. Só aceita endereços do próprio site."""

    def get_next_url(self):
        destino = self.request.POST.get('next') or self.request.GET.get('next')
        if destino and url_has_allowed_host_and_scheme(
            destino, allowed_hosts={self.request.get_host()}, require_https=self.request.is_secure()
        ):
            return destino
        return None

    def get_success_url(self):
        return self.get_next_url() or super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destino = self.get_next_url()
        if destino:
            context['voltar'] = destino
        return context


class ExclusaoMixin(SuccessMessageMixin):
    template_name = 'crud/confirm_delete.html'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'Este registro está em uso e não pode ser excluído.')
            return HttpResponseRedirect(self.get_success_url())


# Equipes

class TeamQuerysetMixin:
    def get_queryset(self):
        return Team.objects.visiveis_para(self.request.user).select_related('manager')


class TeamListView(AdministradorOuGerenteMixin, TeamQuerysetMixin, ListView):
    template_name = 'projects/team_list.html'
    context_object_name = 'equipes'
    paginate_by = ITENS_POR_PAGINA

    def get_queryset(self):
        return super().get_queryset().annotate(total_membros=Count('members')).order_by('name')


class TeamDetailView(AdministradorOuGerenteMixin, TeamQuerysetMixin, DetailView):
    template_name = 'projects/team_detail.html'
    context_object_name = 'equipe'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('members', 'projects')


class TeamCreateView(RetornoMixin, SomenteAdministradorMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('projects:equipes')
    success_message = 'Equipe cadastrada.'
    extra_context = {'titulo': 'Nova equipe', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:equipes')}


class TeamUpdateView(RetornoMixin, SomenteAdministradorMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('projects:equipes')
    success_message = 'Equipe alterada.'
    extra_context = {'titulo': 'Editar equipe', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:equipes')}


class TeamDeleteView(RetornoMixin, SomenteAdministradorMixin, ExclusaoMixin, DeleteView):
    model = Team
    success_url = reverse_lazy('projects:equipes')
    success_message = 'Equipe excluída.'
    extra_context = {'titulo': 'Excluir equipe', 'voltar': reverse_lazy('projects:equipes')}


# Projetos: somente o dono lista, vê, altera e exclui.

class ProjectDonoMixin(AdministradorOuGerenteMixin):
    def get_queryset(self):
        return Project.objects.do_dono(self.request.user).select_related('team', 'created_by')


class ProjectListView(ProjectDonoMixin, FilterView):
    filterset_class = ProjectFilter
    template_name = 'projects/project_list.html'
    context_object_name = 'projetos'
    paginate_by = ITENS_POR_PAGINA

    def get_queryset(self):
        return super().get_queryset().annotate(total_tarefas=Count('stages__tasks')).order_by('name')


class ProjectDetailView(ProjectDonoMixin, DetailView):
    template_name = 'projects/project_detail.html'
    context_object_name = 'projeto'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('assigned_members', 'stages')


class ProjectCreateView(RetornoMixin, AdministradorOuGerenteMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('projects:projetos')
    success_message = 'Projeto cadastrado com quatro estágios.'
    extra_context = {'titulo': 'Novo projeto', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:projetos')}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(RetornoMixin, ProjectDonoMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    form_class = ProjectForm
    success_url = reverse_lazy('projects:projetos')
    success_message = 'Projeto alterado.'
    extra_context = {'titulo': 'Editar projeto', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:projetos')}


class ProjectDeleteView(RetornoMixin, ProjectDonoMixin, ExclusaoMixin, DeleteView):
    success_url = reverse_lazy('projects:projetos')
    success_message = 'Projeto excluído.'
    extra_context = {'titulo': 'Excluir projeto', 'voltar': reverse_lazy('projects:projetos')}


# Estágios

class StageQuerysetMixin(AdministradorOuGerenteMixin):
    def get_queryset(self):
        projetos = Project.objects.com_participacao(self.request.user)
        return Stage.objects.filter(project__in=projetos).select_related('project')


class StageListView(StageQuerysetMixin, ListView):
    template_name = 'projects/stage_list.html'
    context_object_name = 'estagios'
    paginate_by = ITENS_POR_PAGINA

    def get_queryset(self):
        return super().get_queryset().annotate(total_tarefas=Count('tasks')).order_by('project__name', 'order')


class StageDetailView(StageQuerysetMixin, DetailView):
    template_name = 'projects/stage_detail.html'
    context_object_name = 'estagio'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('tasks__assigned_to')


class StageCreateView(RetornoMixin, AdministradorOuGerenteMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = Stage
    form_class = StageForm
    success_url = reverse_lazy('projects:estagios')
    success_message = 'Estágio cadastrado.'
    extra_context = {'titulo': 'Novo estágio', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:estagios')}


class StageUpdateView(RetornoMixin, StageQuerysetMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    form_class = StageForm
    success_url = reverse_lazy('projects:estagios')
    success_message = 'Estágio alterado.'
    extra_context = {'titulo': 'Editar estágio', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:estagios')}


class StageDeleteView(RetornoMixin, StageQuerysetMixin, ExclusaoMixin, DeleteView):
    success_url = reverse_lazy('projects:estagios')
    success_message = 'Estágio excluído.'
    extra_context = {'titulo': 'Excluir estágio', 'voltar': reverse_lazy('projects:estagios')}

    def form_valid(self, form):
        if self.object.tasks.exists():
            messages.error(self.request, 'Mova ou exclua as tarefas antes de excluir este estágio.')
            return HttpResponseRedirect(self.get_success_url())
        return super().form_valid(form)


# Tarefas: visíveis para quem participa do projeto.

class TaskQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.visiveis_para(self.request.user).select_related('stage__project', 'assigned_to')


class TaskListView(TaskQuerysetMixin, FilterView):
    filterset_class = TaskFilter
    template_name = 'projects/task_list.html'
    context_object_name = 'tarefas'
    paginate_by = ITENS_POR_PAGINA


class TaskDetailView(TaskQuerysetMixin, DetailView):
    template_name = 'projects/task_detail.html'
    context_object_name = 'tarefa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['minhas_anotacoes'] = self.object.notes.do_autor(self.request.user)
        context['meus_apontamentos'] = self.object.time_entries.do_autor(self.request.user)
        return context


class TaskCreateView(RetornoMixin, LoginRequiredMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('projects:tarefas')
    success_message = 'Tarefa cadastrada.'
    extra_context = {'titulo': 'Nova tarefa', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:tarefas')}

    def get_initial(self):
        initial = super().get_initial()
        estagio = self.request.GET.get('estagio', '')
        if estagio.isdecimal():
            projetos = Project.objects.com_participacao(self.request.user)
            if Stage.objects.filter(pk=estagio, project__in=projetos).exists():
                initial['stage'] = int(estagio)
        return initial


class TaskUpdateView(RetornoMixin, TaskQuerysetMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    form_class = TaskForm
    success_url = reverse_lazy('projects:tarefas')
    success_message = 'Tarefa alterada.'
    extra_context = {'titulo': 'Editar tarefa', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:tarefas')}


class TaskDeleteView(RetornoMixin, TaskQuerysetMixin, ExclusaoMixin, DeleteView):
    success_url = reverse_lazy('projects:tarefas')
    success_message = 'Tarefa excluída.'
    extra_context = {'titulo': 'Excluir tarefa', 'voltar': reverse_lazy('projects:tarefas')}


# Anotações: privadas do autor.

class NoteAutorMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Note.objects.do_autor(self.request.user).select_related('task__stage__project')


class NoteListView(NoteAutorMixin, ListView):
    template_name = 'projects/note_list.html'
    context_object_name = 'anotacoes'
    paginate_by = ITENS_POR_PAGINA


class NoteDetailView(NoteAutorMixin, DetailView):
    template_name = 'projects/note_detail.html'
    context_object_name = 'anotacao'


class NoteCreateView(RetornoMixin, LoginRequiredMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = Note
    form_class = NoteForm
    success_url = reverse_lazy('projects:anotacoes')
    success_message = 'Anotação cadastrada.'
    extra_context = {'titulo': 'Nova anotação', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:anotacoes')}

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get('tarefa'):
            initial['task'] = self.request.GET['tarefa']
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteUpdateView(RetornoMixin, NoteAutorMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    form_class = NoteForm
    success_url = reverse_lazy('projects:anotacoes')
    success_message = 'Anotação alterada.'
    extra_context = {'titulo': 'Editar anotação', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:anotacoes')}


class NoteDeleteView(RetornoMixin, NoteAutorMixin, ExclusaoMixin, DeleteView):
    success_url = reverse_lazy('projects:anotacoes')
    success_message = 'Anotação excluída.'
    extra_context = {'titulo': 'Excluir anotação', 'voltar': reverse_lazy('projects:anotacoes')}


# Apontamentos de horas: privados do autor.

class TimeEntryAutorMixin(LoginRequiredMixin):
    def get_queryset(self):
        return TimeEntry.objects.do_autor(self.request.user).select_related('task__stage__project')


class TimeEntryListView(TimeEntryAutorMixin, ListView):
    template_name = 'projects/timeentry_list.html'
    context_object_name = 'apontamentos'
    paginate_by = ITENS_POR_PAGINA

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_horas'] = self.get_queryset().aggregate(total=Sum('hours'))['total']
        return context


class TimeEntryDetailView(TimeEntryAutorMixin, DetailView):
    template_name = 'projects/timeentry_detail.html'
    context_object_name = 'apontamento'


class TimeEntryCreateView(RetornoMixin, LoginRequiredMixin, FormComUsuarioMixin, SuccessMessageMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    success_url = reverse_lazy('projects:apontamentos')
    success_message = 'Apontamento cadastrado.'
    extra_context = {'titulo': 'Apontar horas', 'botao': 'Cadastrar', 'voltar': reverse_lazy('projects:apontamentos')}

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get('tarefa'):
            initial['task'] = self.request.GET['tarefa']
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TimeEntryUpdateView(RetornoMixin, TimeEntryAutorMixin, FormComUsuarioMixin, SuccessMessageMixin, UpdateView):
    form_class = TimeEntryForm
    success_url = reverse_lazy('projects:apontamentos')
    success_message = 'Apontamento alterado.'
    extra_context = {'titulo': 'Editar apontamento', 'botao': 'Salvar', 'voltar': reverse_lazy('projects:apontamentos')}


class TimeEntryDeleteView(RetornoMixin, TimeEntryAutorMixin, ExclusaoMixin, DeleteView):
    success_url = reverse_lazy('projects:apontamentos')
    success_message = 'Apontamento excluído.'
    extra_context = {'titulo': 'Excluir apontamento', 'voltar': reverse_lazy('projects:apontamentos')}


# Quadro kanban e movimento

class BoardListView(LoginRequiredMixin, ListView):
    template_name = 'projects/board_list.html'
    context_object_name = 'projetos'
    paginate_by = ITENS_POR_PAGINA

    def get_queryset(self):
        return Project.objects.com_participacao(self.request.user).select_related('team')


class BoardView(LoginRequiredMixin, DetailView):
    template_name = 'projects/board.html'
    context_object_name = 'projeto'

    def get_queryset(self):
        return Project.objects.com_participacao(self.request.user).select_related('team')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        estagios = list(self.object.stages.prefetch_related('tasks__assigned_to'))
        context['colunas'] = [
            {
                'estagio': estagio,
                'anterior': estagios[i - 1] if i > 0 else None,
                'proximo': estagios[i + 1] if i + 1 < len(estagios) else None,
            }
            for i, estagio in enumerate(estagios)
        ]
        context['total_tarefas'] = sum(len(estagio.tasks.all()) for estagio in estagios)
        return context


class TaskMoveView(LoginRequiredMixin, View):
    """Movimento do sistema: leva uma tarefa para outro estágio do mesmo projeto."""

    http_method_names = ['post']

    def post(self, request, pk):
        tarefa = get_object_or_404(Task.objects.visiveis_para(request.user).select_related('stage'), pk=pk)
        projeto_id = tarefa.stage.project_id
        estagio_id = request.POST.get('stage', '')
        destino = None
        if estagio_id.isdecimal():
            destino = Stage.objects.filter(pk=estagio_id, project_id=projeto_id).first()
        if destino is None:
            messages.error(request, 'Escolha um estágio do mesmo projeto.')
        elif destino.pk != tarefa.stage_id:
            tarefa.stage = destino
            tarefa.save(update_fields=['stage', 'updated_at'])
            messages.success(request, f'Tarefa movida para {destino.name}.')
        return redirect('projects:quadro', pk=projeto_id)
