from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PessoaCadastroForm, PessoaForm
from .models import Pessoa


def pessoa_acessivel(request, id, acao):
    pessoa = get_object_or_404(Pessoa, id=id)
    if pessoa.pk != request.user.pk and not request.user.has_perm(f"pessoa.{acao}_pessoa"):
        raise PermissionDenied
    if acao != "view" and pessoa.pk != request.user.pk:
        if (pessoa.is_staff or pessoa.is_superuser) and not request.user.is_superuser:
            raise PermissionDenied
    return pessoa


@login_required
@permission_required("pessoa.view_pessoa", raise_exception=True)
def listar_pessoas(request):
    pessoas = Pessoa.objects.order_by("nome", "pk")
    return render(request, "pessoa/listar.html", {"pessoas": pessoas})


@require_http_methods(["GET", "POST"])
def cadastrar(request):
    if request.user.is_authenticated:
        return redirect("listar_produtos")
    form = PessoaCadastroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, "Usuário ou CPF já cadastrado. Confira os dados.")
        else:
            messages.success(request, "Cadastro realizado. Entre com seu usuário e senha.")
            return redirect("login_pessoa")
    return render(request, "pessoa/cadastro.html", {"form": form})


@login_required
@permission_required("pessoa.add_pessoa", raise_exception=True)
@require_http_methods(["GET", "POST"])
def criar_pessoa(request):
    form = PessoaCadastroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, "Usuário ou CPF já cadastrado. Confira os dados.")
        else:
            messages.success(request, "Pessoa cadastrada com sucesso.")
            return redirect("listar_produtos")
    return render(request, "pessoa/criar.html", {"form": form})


@login_required
def minha_conta(request):
    pessoa = Pessoa.objects.filter(pk=request.user.pk).first()
    if pessoa is None:
        messages.info(request, "Esta conta administrativa não possui cadastro de cliente.")
        return redirect("listar_produtos")
    return redirect("detalhar_pessoa", id=pessoa.pk)


@login_required
def detalhar_pessoa(request, id):
    pessoa = pessoa_acessivel(request, id, "view")
    return render(request, "pessoa/detalhar.html", {"pessoa": pessoa})


@login_required
@require_http_methods(["GET", "POST"])
def editar_pessoa(request, id):
    pessoa = pessoa_acessivel(request, id, "change")
    form = PessoaForm(request.POST if request.method == "POST" else None, instance=pessoa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil atualizado.")
        return redirect("minha_conta" if pessoa.pk == request.user.pk else "listar_produtos")
    return render(request, "pessoa/editar.html", {"form": form, "pessoa": pessoa})


@login_required
@require_http_methods(["GET", "POST"])
def excluir_pessoa(request, id):
    pessoa = pessoa_acessivel(request, id, "delete")
    if request.method == "POST":
        propria_conta = pessoa.pk == request.user.pk
        try:
            pessoa.delete()
        except ProtectedError:
            messages.error(request, "Esta pessoa possui pedidos e não pode ser excluída.")
        else:
            if propria_conta:
                logout(request)
            messages.success(request, "Pessoa excluída.")
            return redirect("listar_produtos")
    return render(request, "pessoa/excluir.html", {"pessoa": pessoa})
