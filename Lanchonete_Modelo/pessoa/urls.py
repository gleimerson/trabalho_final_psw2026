from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views


urlpatterns = [
    path('cadastro/', views.cadastrar, name='cadastro'),
    path('minha-conta/', views.minha_conta, name='minha_conta'),
    path('senha/', auth_views.PasswordChangeView.as_view(
        template_name='pessoa/senha.html', success_url=reverse_lazy('senha_alterada')
    ), name='alterar_senha'),
    path('senha/alterada/', auth_views.PasswordChangeDoneView.as_view(
        template_name='pessoa/senha_alterada.html'
    ), name='senha_alterada'),
    path('', views.listar_pessoas, name='listar_pessoas'),
    path('criar/', views.criar_pessoa, name='criar_pessoa'),
    path('<int:id>/', views.detalhar_pessoa, name='detalhar_pessoa'),
    path('<int:id>/editar/', views.editar_pessoa, name='editar_pessoa'),
    path('<int:id>/excluir/', views.excluir_pessoa, name='excluir_pessoa'),

    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login_pessoa'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout_pessoa'),
]

# Endereços antigos continuam funcionando, inclusive em formulários POST.
urlpatterns += [
    path('pessoas/', views.listar_pessoas),
    path('pessoas/criar/', views.criar_pessoa),
    path('pessoas/<int:id>/', views.detalhar_pessoa),
    path('pessoas/<int:id>/editar/', views.editar_pessoa),
    path('pessoas/<int:id>/excluir/', views.excluir_pessoa),
]
