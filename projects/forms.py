from django import forms

from accounts.constants import DESENVOLVEDOR, GERENTE
from accounts.models import User

from .models import Note, Project, Stage, Task, Team, TimeEntry


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        super().__init__(format='%Y-%m-%d', **kwargs)


class MembrosField(forms.ModelMultipleChoiceField):
    """Dropdown de seleção múltipla com busca: cada pessoa escolhida vira uma pílula no campo (Select2 em app.js).

    Sem JavaScript continua sendo um <select multiple> comum.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', forms.SelectMultiple(attrs={
            'data-pilulas': '1', 'data-placeholder': 'Busque e selecione pelo nome ou e-mail',
        }))
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return f'{obj} · {obj.email}'


class TeamForm(forms.ModelForm):
    members = MembrosField(
        label='Membros', queryset=User.objects.none(), required=False,
        help_text='Escolha quantos desenvolvedores quiser; cada um vira uma etiqueta no campo. Clique no × para remover.',
    )

    class Meta:
        model = Team
        fields = ['name', 'manager', 'members']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        ativos = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['manager'].queryset = ativos.filter(groups__name=GERENTE)
        self.fields['members'].queryset = ativos.filter(groups__name=DESENVOLVEDOR)


class ProjectForm(forms.ModelForm):
    assigned_members = MembrosField(
        label='Membros atribuídos', queryset=User.objects.none(), required=False,
        help_text='Escolha quem trabalha no projeto; só valem o gerente e os membros da equipe escolhida.',
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'team', 'assigned_members', 'start_date', 'end_date']
        widgets = {'start_date': DateInput(), 'end_date': DateInput()}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Gerente só cria projetos nas equipes que gerencia.
        self.fields['team'].queryset = Team.objects.visiveis_para(user)
        self.fields['assigned_members'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')

    def clean(self):
        cleaned = super().clean()
        team = cleaned.get('team')
        membros = cleaned.get('assigned_members')
        if team and membros:
            validos = set(team.members.values_list('pk', flat=True)) | {team.manager_id}
            if any(m.pk not in validos for m in membros):
                self.add_error('assigned_members', 'Os membros atribuídos precisam pertencer à equipe.')
        return cleaned


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['project', 'name', 'stage_type', 'order']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.com_participacao(user).select_related('team')
        if self.instance.pk:
            # Tipo e projeto não mudam depois da criação.
            self.fields['project'].disabled = True
            self.fields['stage_type'].disabled = True


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'stage', 'assigned_to', 'due_date', 'priority']
        widgets = {'due_date': DateInput()}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        projetos = Project.objects.com_participacao(user)
        self.fields['stage'].queryset = Stage.objects.filter(project__in=projetos).select_related('project')
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['task', 'content']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Task.objects.visiveis_para(user)


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['task', 'date', 'hours', 'description']
        widgets = {'date': DateInput()}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Task.objects.visiveis_para(user)
