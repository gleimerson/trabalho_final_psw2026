from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Pessoa
from .validators import normalizar_cpf


class CPFFormMixin:
    def clean_cpf(self):
        cpf = normalizar_cpf(self.cleaned_data["cpf"])
        if Pessoa.objects.filter(cpf=cpf).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este CPF já está cadastrado.")
        return cpf


class PessoaCadastroForm(CPFFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Pessoa
        fields = ("username", "nome", "cpf", "email")

    def clean_username(self):
        username = self.cleaned_data["username"]
        # Também considera administradores que não têm uma linha em Pessoa.
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nome de usuário já está cadastrado.")
        return username


class PessoaForm(CPFFormMixin, forms.ModelForm):
    """Edição de perfil sem campos de senha ou elevação de privilégios."""

    class Meta:
        model = Pessoa
        fields = ("nome", "cpf", "email")


class PessoaAdminChangeForm(CPFFormMixin, UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Pessoa
