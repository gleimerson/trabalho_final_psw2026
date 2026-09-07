from django.db import models
from pessoa.models import Pessoa
from produtos.models import Produto
# Create your models here.
class Pedido(models.Model):
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    valor_total = models.FloatField()

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)

class PedidoProduto(models.Model):
   
    preco_unitario = models.FloatField()
    quantidade = models.IntegerField()

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)