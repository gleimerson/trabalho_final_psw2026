from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods


from pessoa.models import Pessoa
from .forms import PedidoForm, PedidoProdutoFormSet
from .models import Pedido


def pedidos_acessiveis(user, acao="view"):
    pedidos = Pedido.objects.select_related("pessoa")
    if not user.has_perm(f"pedidos.{acao}_pedido"):
        pedidos = pedidos.filter(pessoa_id=user.pk)
    return pedidos


def verificar_edicao(user, pedido, acao):
    if not user.has_perm(f"pedidos.{acao}_pedido") and pedido.status != Pedido.Status.NOVO:
        raise PermissionDenied("Somente pedidos novos podem ser alterados pelo cliente.")



@require_http_methods(["GET", "HEAD"])
def listar_pedidos(request):
    pedidos = pedidos_acessiveis(request.user).order_by("-data_pedido", "-pk")
    return render(request, "pedidos/listar.html", {"pedidos": pedidos})


def formulario_pedido(request, pedido, template):
    data = request.POST if request.method == "POST" else None
    form = PedidoForm(data, instance=pedido, user=request.user)
    formset = PedidoProdutoFormSet(data, instance=pedido, prefix="itens")
    if request.method == "POST":
        valido = form.is_valid()
        itens_validos = formset.is_valid()
        if valido and itens_validos:
            form.save()
            formset.save()
            pedido.recalcular_total()
            messages.success(request, "Pedido salvo com sucesso.")
            return redirect("listar_pedidos")
    return render(request, template, {"form": form, "formset": formset, "pedido": pedido})



@require_http_methods(["GET", "POST"])
@transaction.atomic
def criar_pedido(request):
    if not request.user.has_perm("pedidos.add_pedido") and not Pessoa.objects.filter(pk=request.user.pk).exists():
        messages.error(request, "Esta conta não possui cadastro de cliente nem permissão para cadastrar pedidos.")
        return redirect("listar_pedidos")
    return formulario_pedido(request, Pedido(), "pedidos/criar.html")



def detalhar_pedido(request, id):
    pedido = get_object_or_404(pedidos_acessiveis(request.user), id=id)
    return render(request, "pedidos/detalhar.html", {"pedido": pedido, "itens": pedido.itens.select_related("produto")})



@require_http_methods(["GET", "POST"])
@transaction.atomic
def editar_pedido(request, id):
    pedido = get_object_or_404(pedidos_acessiveis(request.user, "change").select_for_update(), id=id)
    verificar_edicao(request.user, pedido, "change")
    return formulario_pedido(request, pedido, "pedidos/editar.html")



@require_http_methods(["GET", "POST"])
@transaction.atomic
def excluir_pedido(request, id):
    pedido = get_object_or_404(pedidos_acessiveis(request.user, "delete").select_for_update(), id=id)
    verificar_edicao(request.user, pedido, "delete")
    if request.method == "POST":
        pedido.delete()
        messages.success(request, "Pedido excluído.")
        return redirect("listar_pedidos")
    return render(request, "pedidos/excluir.html", {"pedido": pedido})
