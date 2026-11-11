from django import forms

from .models import ConfiguracaoIA, CotaUsuario


class ConfiguracaoIAForm(forms.ModelForm):
    chave_api = forms.CharField(
        label='Chave da API do Gemini (Google AI Studio)', required=False, strip=True,
        widget=forms.PasswordInput(render_value=False, attrs={'autocomplete': 'off'}),
        help_text='Deixe em branco para manter a chave atual. Ela é guardada cifrada.',
    )
    remover_chave = forms.BooleanField(label='Remover a chave cadastrada', required=False)

    class Meta:
        model = ConfiguracaoIA
        fields = ['ativo', 'modelo', 'esforco', 'max_tokens', 'cota_mensal_padrao', 'instrucoes']
        widgets = {'instrucoes': forms.Textarea(attrs={'rows': 10})}

    def save(self, commit=True):
        config = super().save(commit=False)
        if self.cleaned_data.get('remover_chave'):
            config.definir_chave('')
        elif self.cleaned_data.get('chave_api'):
            config.definir_chave(self.cleaned_data['chave_api'])
        if commit:
            config.save()
        return config


class CotaUsuarioForm(forms.ModelForm):
    class Meta:
        model = CotaUsuario
        fields = ['limite_mensal']
