from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria
from .forms import CategoriaForm, ProdutoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_http_methods




@require_http_methods(["GET", "HEAD"])
def listar_categorias(request):
    categorias = Categoria.objects.order_by("nome", "pk")

    return render(
        request,
        'categorias/listar.html',
        {'categorias': categorias}
    )

@login_required
@permission_required("produtos.add_categoria", raise_exception=True)
@require_http_methods(["GET", "POST"])
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Categoria criada com sucesso.")
            return redirect('listar_categorias')

    else:
        form = CategoriaForm()

    return render(
        request,
        'categorias/criar.html',
        {'form': form}
    )



@require_http_methods(["GET", "HEAD"])
def detalhar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    produtos = Produto.objects.filter(categoria_id=id)

    return render(request, 'categorias/detalhar.html', {
        'categoria': categoria,
        'produtos': produtos
    })



@require_http_methods(["GET", "POST"])
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect('detalhar_categoria', id=categoria.id)
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'categorias/editar.html', {'form': form, 'categoria': categoria})

@login_required
@permission_required("produtos.delete_categoria", raise_exception=True)
@require_http_methods(["GET", "POST"])
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        try:
            categoria.delete()
        except ProtectedError:
            messages.error(request, "Este registro está em uso e não pode ser excluído.")
        else:
            messages.success(request, "Categoria excluída com sucesso.")
            return redirect('listar_categorias')

    return render(request, 'categorias/excluir.html', {'categoria': categoria})

@require_http_methods(["GET", "HEAD"])
def listar_produtos(request):
    produtos = Produto.objects.select_related("categoria").order_by("nome", "pk")
    return render(request, 'produtos/listar.html', {'produtos': produtos})

@login_required
@permission_required("produtos.add_produto", raise_exception=True)
@require_http_methods(["GET", "POST"])
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            produto = form.save()
            messages.success(request, "Produto criado com sucesso.")
            return redirect('detalhar_produto', id=produto.id)
    else:
        form = ProdutoForm()

    return render(request, 'produtos/criar.html', {'form': form})



@require_http_methods(["GET", "HEAD"])
def detalhar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'produtos/detalhar.html', {'produto': produto})

@login_required
@permission_required("produtos.change_produto", raise_exception=True)
@require_http_methods(["GET", "POST"])
def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso.")
            return redirect('detalhar_produto', id=produto.id)
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produtos/editar.html', {'form': form, 'produto': produto})

@login_required
@permission_required("produtos.delete_produto", raise_exception=True)
@require_http_methods(["GET", "POST"])
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        try:
            produto.delete()
        except ProtectedError:
            messages.error(request, "Este registro está em uso e não pode ser excluído.")
        else:
            messages.success(request, "Produto excluído com sucesso.")
            return redirect('listar_produtos')

    return render(request, 'produtos/excluir.html', {'produto': produto})
