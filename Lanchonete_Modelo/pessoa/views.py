from django.shortcuts import render, redirect, get_object_or_404
from .models import Pessoa
from .forms import PessoaForm
from django.contrib.auth import authenticate, login, logout

def listar_pessoas(request):
    pessoas = Pessoa.objects.all()
    return render(request, 'pessoas/listar.html', {'pessoas': pessoas})


def criar_pessoa(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)

        if form.is_valid():
            pessoa = form.save()
            return redirect('detalhar_pessoa', id=pessoa.id)
    else:
        form = PessoaForm()

    return render(request, 'pessoas/criar.html', {'form': form})


def detalhar_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    return render(request, 'pessoas/detalhar.html', {'pessoa': pessoa})


def editar_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)

    if request.method == 'POST':
        form = PessoaForm(request.POST, instance=pessoa)

        if form.is_valid():
            form.save()
            return redirect('detalhar_pessoa', id=pessoa.id)
    else:
        form = PessoaForm(instance=pessoa)

    return render(request, 'pessoas/editar.html', {'form': form, 'pessoa': pessoa})


def excluir_pessoa(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)

    if request.method == 'POST':
        pessoa.delete()
        return redirect('listar_pessoas')

    return render(request, 'pessoas/excluir.html', {'pessoa': pessoa})



def login_pessoa(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        pessoa = authenticate(request, username=username, password=password)

        if pessoa is not None:
            login(request, pessoa)
            return redirect('listar_produtos')

        return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos.'})

    return render(request, 'login.html')


def logout_pessoa(request):
    logout(request)
    return redirect('login_pessoa')
