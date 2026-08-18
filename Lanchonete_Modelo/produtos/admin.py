from django.contrib import admin
from .models import Categoria, Pessoa, Produto, Pedido, PedidoProduto

admin.site.register(Categoria)
admin.site.register(Pessoa)
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(PedidoProduto)
