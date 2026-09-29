from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido
from .forms import PedidoForm
from django.contrib.auth.decorators import login_required


@login_required
def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos/listar.html', {'pedidos': pedidos})

@login_required
def criar_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
            pedido = form.save()
            return redirect('detalhar_pedido', id=pedido.id)

    else:
        form = PedidoForm()

    return render(request, 'pedidos/criar.html', {'form': form})

@login_required
def detalhar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    return render(request, 'pedidos/detalhar.html', {'pedido': pedido})

@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)

        if form.is_valid():
            form.save()
            return redirect('detalhar_pedido', id=pedido.id)

    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar.html', {'form': form, 'pedido': pedido})

@login_required
def excluir_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if request.method == 'POST':
        pedido.delete()
        return redirect('listar_pedidos')

    return render(request, 'pedidos/excluir.html', {'pedido': pedido})