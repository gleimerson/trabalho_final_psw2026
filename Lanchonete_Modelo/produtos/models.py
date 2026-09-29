from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    descricao = models.CharField(max_length=255)
    disponivel = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(preco__gte=0), name="produto_preco_nao_negativo")]

    def __str__(self):
        return self.nome
