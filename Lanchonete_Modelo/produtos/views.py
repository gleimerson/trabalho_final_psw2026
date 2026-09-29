from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria
from .forms import CategoriaForm, ProdutoForm
from django.contrib.auth.decorators import login_required



def listar_categorias(request):
    categorias = Categoria.objects.all()

    return render(
        request,
        'categorias/listar.html',
        {'categorias': categorias}
    )

@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('listar_categorias')

    else:
        form = CategoriaForm()

    return render(
        request,
        'categorias/criar.html',
        {'form': form}
    )

def detalhar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    return render(request, 'categorias/detalhar.html', {'categoria': categoria})

@login_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            return redirect('detalhar_categoria', id=categoria.id)
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'categorias/editar.html', {'form': form, 'categoria': categoria})

@login_required
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        categoria.delete()
        return redirect('listar_categorias')

    return render(request, 'categorias/excluir.html', {'categoria': categoria})

def listar_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/listar.html', {'produtos': produtos})

@login_required
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            produto = form.save()
            return redirect('detalhar_produto', id=produto.id)
    else:
        form = ProdutoForm()

    return render(request, 'produtos/criar.html', {'form': form})


def detalhar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'produtos/detalhar.html', {'produto': produto})

@login_required
def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():
            form.save()
            return redirect('detalhar_produto', id=produto.id)
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produtos/editar.html', {'form': form, 'produto': produto})

@login_required
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        produto.delete()
        return redirect('listar_produtos')

    return render(request, 'produtos/excluir.html', {'produto': produto})