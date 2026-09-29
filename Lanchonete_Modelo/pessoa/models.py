from django.contrib.auth.models import User
from django.db import models

from .validators import normalizar_cpf, validar_cpf


class Pessoa(User):
    """Especialização do User por herança multitable, conforme o diagrama."""

    nome = models.CharField(max_length=100)
    cpf = models.CharField("CPF", max_length=14, unique=True, validators=[validar_cpf])

    class Meta:
        verbose_name = "pessoa"
        verbose_name_plural = "pessoas"

    def clean(self):
        super().clean()
        self.cpf = normalizar_cpf(self.cpf)

    def __str__(self):
        return self.nome or self.username
