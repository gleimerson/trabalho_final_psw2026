from django.urls import path
from . import views


urlpatterns = [
    path('pessoas/', views.listar_pessoas, name='listar_pessoas'),
    path('pessoas/criar/', views.criar_pessoa, name='criar_pessoa'),
    path('pessoas/<int:id>/', views.detalhar_pessoa, name='detalhar_pessoa'),
    path('pessoas/<int:id>/editar/', views.editar_pessoa, name='editar_pessoa'),
    path('pessoas/<int:id>/excluir/', views.excluir_pessoa, name='excluir_pessoa'),

    path('login/', views.login_pessoa, name='login_pessoa'),
    path('logout/', views.logout_pessoa, name='logout_pessoa'),
]