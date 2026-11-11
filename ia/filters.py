import django_filters

from accounts.models import User

from .models import ChamadaIA, Origem, Status


class ChamadaIAFilter(django_filters.FilterSet):
    usuario = django_filters.ModelChoiceFilter(label='Usuário', queryset=User.objects.all(), empty_label='Todos')
    status = django_filters.ChoiceFilter(label='Situação', choices=Status.choices, empty_label='Todas')
    origem = django_filters.ChoiceFilter(label='Origem', choices=Origem.choices, empty_label='Todas')

    class Meta:
        model = ChamadaIA
        fields = ['usuario', 'status', 'origem']
