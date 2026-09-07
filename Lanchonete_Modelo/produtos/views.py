from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Produto, Categoria
from .forms import CategoriaForm, ProdutoForm



def listar_categorias(request):
    categorias = Categoria.objects.all()

    return render(
        request,
        'categorias/listar.html',
        {'categorias': categorias}
    )

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
