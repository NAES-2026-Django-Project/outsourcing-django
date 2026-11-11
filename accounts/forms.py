from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction

from .constants import DESENVOLVEDOR, GRUPOS
from .models import User


class CadastroForm(UserCreationForm):
    """Cadastro público: não expõe grupo, todo novo usuário é Desenvolvedor."""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.add(Group.objects.get(name=DESENVOLVEDOR))
        return user


class DadosPessoaisForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']


class PapelUsuarioForm(forms.ModelForm):
    """Somente administradores alteram o papel e a situação de um usuário."""

    papel = forms.ChoiceField(label='Papel', choices=[(g, g) for g in GRUPOS])

    class Meta:
        model = User
        fields = ['is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['papel'].initial = self.instance.papel

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.set([Group.objects.get(name=self.cleaned_data['papel'])])
        return user
