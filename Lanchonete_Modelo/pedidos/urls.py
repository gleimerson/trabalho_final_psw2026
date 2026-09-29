from django.urls import path
from . import views


urlpatterns = [
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/criar/', views.criar_pedido, name='criar_pedido'),
    path('pedidos/<int:id>/', views.detalhar_pedido, name='detalhar_pedido'),
    path('pedidos/<int:id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/<int:id>/excluir/', views.excluir_pedido, name='excluir_pedido'),
]