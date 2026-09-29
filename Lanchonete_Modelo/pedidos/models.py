from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Pedido(models.Model):
    class Status(models.TextChoices):
        NOVO = "Novo", "Novo"
        PREPARO = "Em preparo", "Em preparo"
        PRONTO = "Pronto", "Pronto"
        ENTREGUE = "Entregue", "Entregue"
        CANCELADO = "Cancelado", "Cancelado"

    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.NOVO)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    pessoa = models.ForeignKey("pessoa.Pessoa", on_delete=models.PROTECT)
    produtos = models.ManyToManyField("produtos.Produto", through="PedidoProduto", related_name="pedidos")

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(valor_total__gte=0), name="pedido_total_nao_negativo")]

    def recalcular_total(self):
        self.valor_total = sum((item.subtotal for item in self.itens.all()), Decimal("0.00"))
        self.save(update_fields=["valor_total"])

    def __str__(self):
        return f"Pedido #{self.pk}"


class PedidoProduto(models.Model):
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantidade__gte=1), name="item_quantidade_positiva"),
            models.CheckConstraint(condition=models.Q(preco_unitario__gte=0), name="item_preco_nao_negativo"),
            models.UniqueConstraint(fields=["pedido", "produto"], name="item_produto_unico_por_pedido"),
        ]

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade} × {self.produto}"
