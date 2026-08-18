from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=255)

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.FloatField()
    descricao = models.CharField(max_length=255)
    disponivel = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
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
