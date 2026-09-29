from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import PessoaAdminChangeForm, PessoaCadastroForm
from .models import Pessoa


@admin.register(Pessoa)
class PessoaAdmin(UserAdmin):
    add_form = PessoaCadastroForm
    form = PessoaAdminChangeForm
    list_display = ("username", "nome", "email", "is_active", "is_staff")
    search_fields = ("username", "nome", "cpf", "email")
    fieldsets = UserAdmin.fieldsets + (("Dados da pessoa", {"fields": ("nome", "cpf")}),)
    add_fieldsets = ((None, {"classes": ("wide",), "fields": (
        "username", "nome", "cpf", "email", "password1", "password2",
    )}),)

    # A edição de User inclui grupos, permissões e flags administrativas.
    # Funcionários gerenciam dados pessoais nas views, sem esses campos.
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
