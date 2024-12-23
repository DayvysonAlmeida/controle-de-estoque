# estoque/forms.py

from django import forms
from .models import Equipamento, CATEGORIAS
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nome')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['nome', 'categoria', 'tombamento', 'status', 'descricao', 'setor']
        widgets = {
            'categoria': forms.Select(choices=CATEGORIAS),
        }

class EquipamentoBuscaForm(forms.Form):
    query = forms.CharField(required=False, label='Buscar por Nome')
    setor = forms.CharField(required=False, label='Filtrar por Setor')
    tombamento = forms.CharField(required=False, label='Filtrar por Tombamento')
    categoria = forms.ChoiceField(
        choices=[('', 'Todas as Categorias')] + [(categoria, categoria) for categoria in Equipamento.objects.values_list('categoria', flat=True).distinct()],
        required=False,
        label='Filtrar por Categoria'
    )
