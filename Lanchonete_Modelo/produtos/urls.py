from django.urls import path
from . import views


urlpatterns = [
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/<int:id>/', views.detalhar_categoria, name='detalhar_categoria'),
    path('categorias/<int:id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:id>/excluir/', views.excluir_categoria, name='excluir_categoria'),

    path('', views.listar_produtos, name='listar_produtos'),
    path('criar/', views.criar_produto, name='criar_produto'),
    path('<int:id>/', views.detalhar_produto, name='detalhar_produto'),
    path('<int:id>/editar/', views.editar_produto, name='editar_produto'),
    path('<int:id>/excluir/', views.excluir_produto, name='excluir_produto'),
]

# Endereços antigos continuam funcionando, inclusive em formulários POST.
urlpatterns += [
    path('produtos/', views.listar_produtos),
    path('produtos/criar/', views.criar_produto),
    path('produtos/<int:id>/', views.detalhar_produto),
    path('produtos/<int:id>/editar/', views.editar_produto),
    path('produtos/<int:id>/excluir/', views.excluir_produto),
]
