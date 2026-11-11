from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True


class TeamQuerySet(models.QuerySet):
    def visiveis_para(self, user):
        if user.eh_administrador:
            return self
        return self.filter(manager=user)


class Team(BaseModel):
    name = models.CharField('nome', max_length=100, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='managed_teams', verbose_name='gerente',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='teams', verbose_name='membros',
    )

    objects = TeamQuerySet.as_manager()

    class Meta:
        verbose_name = 'equipe'
        verbose_name_plural = 'equipes'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectQuerySet(models.QuerySet):
    def do_dono(self, user):
        """Projetos que o usuário cadastrou. Administradores veem todos."""
        if user.eh_administrador:
            return self
        return self.filter(created_by=user)

    def com_participacao(self, user):
        """Projetos em que o usuário trabalha, usados no quadro e nas tarefas."""
        if user.eh_administrador:
            return self
        return self.filter(
            Q(created_by=user) | Q(team__manager=user) | Q(assigned_members=user)
        ).distinct()


class Project(BaseModel):
    name = models.CharField('nome', max_length=150)
    description = models.TextField('descrição', blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='projects', verbose_name='equipe')
    assigned_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='assigned_projects', verbose_name='membros atribuídos',
    )
    start_date = models.DateField('início')
    end_date = models.DateField('término', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_projects', verbose_name='criado por',
    )

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = 'projeto'
        verbose_name_plural = 'projetos'
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'O término não pode ser anterior ao início.'})


class StageType(models.TextChoices):
    BACKLOG = 'backlog', 'Backlog'
    DOING = 'doing', 'Em andamento'
    DONE = 'done', 'Concluído'
    APPROVED = 'approved', 'Aprovado'


class Stage(BaseModel):
    name = models.CharField('nome', max_length=50)
    stage_type = models.CharField('tipo', max_length=10, choices=StageType.choices, default=StageType.BACKLOG)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stages', verbose_name='projeto')
    order = models.PositiveIntegerField('ordem')

    class Meta:
        verbose_name = 'estágio'
        verbose_name_plural = 'estágios'
        ordering = ['project', 'order']
        constraints = [
            models.UniqueConstraint(fields=['project', 'order'], name='estagio_ordem_unica_por_projeto'),
        ]

    def __str__(self):
        return f'{self.project} / {self.name}'


class TaskQuerySet(models.QuerySet):
    def visiveis_para(self, user):
        return self.filter(stage__project__in=Project.objects.com_participacao(user))


class Priority(models.TextChoices):
    LOW = 'low', 'Baixa'
    MEDIUM = 'medium', 'Média'
    HIGH = 'high', 'Alta'
    URGENT = 'urgent', 'Urgente'


class Task(BaseModel):
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição', blank=True)
    # A regra "estágio com tarefas não pode ser excluído" fica em StageDeleteView.
    # CASCADE permite excluir um projeto inteiro com seus estágios e tarefas.
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='tasks', verbose_name='estágio')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='my_tasks', verbose_name='responsável',
    )
    due_date = models.DateField('prazo', null=True, blank=True)
    priority = models.CharField('prioridade', max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    objects = TaskQuerySet.as_manager()

    class Meta:
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title

    def clean(self):
        if not self.assigned_to_id or not self.stage_id:
            return
        project = self.stage.project
        participa = (
            project.team.manager_id == self.assigned_to_id
            or project.assigned_members.filter(pk=self.assigned_to_id).exists()
        )
        if not participa:
            raise ValidationError({'assigned_to': 'O responsável precisa participar do projeto.'})


class NoteQuerySet(models.QuerySet):
    def do_autor(self, user):
        """Anotações são privadas: nem administradores veem as de outras pessoas."""
        return self.filter(author=user)


class Note(BaseModel):
    content = models.TextField('conteúdo')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes', verbose_name='tarefa')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_notes', verbose_name='autor',
    )

    objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = 'anotação'
        verbose_name_plural = 'anotações'
        ordering = ['-created_at']

    def __str__(self):
        return f'Anotação em {self.task}'


class TimeEntryQuerySet(models.QuerySet):
    def do_autor(self, user):
        """Apontamentos são privados: nem administradores veem os de outras pessoas."""
        return self.filter(author=user)


class TimeEntry(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries', verbose_name='tarefa')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_entries', verbose_name='autor',
    )
    date = models.DateField('data', default=timezone.localdate)
    hours = models.DecimalField(
        'horas', max_digits=4, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.25')), MaxValueValidator(Decimal('24'))],
    )
    description = models.CharField('descrição', max_length=200, blank=True)

    objects = TimeEntryQuerySet.as_manager()

    class Meta:
        verbose_name = 'apontamento de horas'
        verbose_name_plural = 'apontamentos de horas'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.hours}h em {self.task}'
