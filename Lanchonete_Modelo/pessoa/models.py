from django.contrib.auth.models import User
from django.db import models


class Pessoa(User):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)