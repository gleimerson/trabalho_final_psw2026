"""Validação local do formato e dos dígitos verificadores do CPF."""

import re

from django.core.exceptions import ValidationError


def normalizar_cpf(valor):
    valor = str(valor).strip()
    if not re.fullmatch(r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})", valor):
        raise ValidationError("Informe um CPF com 11 dígitos, com ou sem pontuação.")
    cpf = re.sub(r"[.-]", "", valor)
    if len(set(cpf)) == 1:
        raise ValidationError("Informe um CPF válido.")
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[tamanho]):
            raise ValidationError("Informe um CPF válido.")
    return cpf


def validar_cpf(valor):
    normalizar_cpf(valor)
