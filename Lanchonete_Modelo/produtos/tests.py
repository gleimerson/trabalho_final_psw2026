"""Regressões de navegação, templates e imagens de produtos."""

from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from pedidos.models import Pedido
from pessoa.models import Pessoa
from .models import Categoria, Produto


class NavegacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pessoa = Pessoa.objects.create_user(
            username="cliente", password="senha-teste", nome="Cliente", cpf="52998224725", is_staff=True, is_superuser=True
        )
        cls.categoria = Categoria.objects.create(nome="Lanches", descricao="Lanches")
        cls.produto = Produto.objects.create(
            nome="Sanduíche", preco=12.5, descricao="Lanche", categoria=cls.categoria
        )
        cls.pedido = Pedido.objects.create(
            pessoa=cls.pessoa, status="Novo", valor_total=12.5
        )

    def test_rotas_canonicas_e_inicio(self):
        for nome, caminho in (
            ("listar_produtos", "/produtos/"),
            ("listar_pessoas", "/pessoas/"),
            ("listar_pedidos", "/pedidos/"),
            ("listar_categorias", "/produtos/categorias/"),
        ):
            with self.subTest(nome=nome):
                self.assertEqual(reverse(nome), caminho)
        self.assertRedirects(self.client.get("/"), "/produtos/")

    def test_paginas_renderizam_layout_e_templates(self):
        self.client.force_login(self.pessoa)
        for singular, plural, objeto in (
            ("pessoa", "pessoas", self.pessoa),
            ("produto", "produtos", self.produto),
            ("categoria", "categorias", self.categoria),
            ("pedido", "pedidos", self.pedido),
        ):
            rotas = [(f"listar_{plural}", []), (f"criar_{singular}", [])]
            rotas += [(f"{acao}_{singular}", [objeto.pk]) for acao in ("detalhar", "editar", "excluir")]
            for nome, args in rotas:
                with self.subTest(nome=nome):
                    resposta = self.client.get(reverse(nome, args=args))
                    self.assertEqual(resposta.status_code, 200)
                    self.assertTemplateUsed(resposta, "base.html")
                    self.assertContains(resposta, 'css/site.css')

    def test_rotas_antigas_e_post_continuam_funcionando(self):
        self.client.force_login(self.pessoa)
        for caminho in ("/pessoas/pessoas/", "/produtos/produtos/", "/pedidos/pedidos/"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 200)
        resposta = self.client.post(
            f"/produtos/produtos/{self.produto.pk}/editar/",
            {"nome": "Atualizado", "descricao": "Lanche", "preco": "15.00", "categoria": self.categoria.pk},
        )
        self.assertRedirects(resposta, reverse("detalhar_produto", args=[self.produto.pk]))
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.nome, "Atualizado")

    def test_login_e_acesso_protegido(self):
        self.assertTemplateUsed(self.client.get(reverse("login_pessoa")), "base.html")
        destino = reverse("criar_produto")
        self.assertRedirects(self.client.get(destino), f"/pessoas/login/?next={destino}")
        resposta = self.client.post(reverse("login_pessoa"), {"username": "cliente", "password": "senha-teste"})
        self.assertRedirects(resposta, reverse("listar_produtos"))

    def test_upload_de_imagem_no_cadastro(self):
        self.client.force_login(self.pessoa)
        buffer = BytesIO()
        Image.new("RGB", (2, 2)).save(buffer, format="PNG")
        imagem = SimpleUploadedFile("lanche.png", buffer.getvalue(), content_type="image/png")
        with TemporaryDirectory() as pasta, override_settings(MEDIA_ROOT=pasta):
            resposta = self.client.post(reverse("criar_produto"), {
                "nome": "Com imagem", "descricao": "Lanche", "preco": "10.00",
                "categoria": self.categoria.pk, "imagem": imagem,
            })
            produto = Produto.objects.get(nome="Com imagem")
            self.assertRedirects(resposta, reverse("detalhar_produto", args=[produto.pk]))
            self.assertTrue(produto.imagem.storage.exists(produto.imagem.name))
            self.assertTrue(produto.imagem.url.startswith("/media/produtos/"))


class CatalogoPermissoesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = Pessoa.objects.create_user(username="comum", nome="Cliente", cpf="11144477735")
        cls.categoria = Categoria.objects.create(nome="Lanches", descricao="Lanches")
        cls.produto = Produto.objects.create(nome="Lanche", preco="10.00", descricao="Lanche", categoria=cls.categoria)

    def test_cliente_nao_modifica_catalogo(self):
        self.client.force_login(self.cliente)
        for model, objeto in [("produto", self.produto), ("categoria", self.categoria)]:
            for acao in ("criar", "editar", "excluir"):
                args = [] if acao == "criar" else [objeto.pk]
                with self.subTest(model=model, acao=acao):
                    self.assertEqual(self.client.post(reverse(f"{acao}_{model}", args=args)).status_code, 403)

    def test_permissao_individual_de_criar_categoria(self):
        from django.contrib.auth.models import Permission
        self.cliente.user_permissions.add(Permission.objects.get(content_type__app_label="produtos", codename="add_categoria"))
        self.client.force_login(self.cliente)
        resposta = self.client.post(reverse("criar_categoria"), {"nome": "Bebidas", "descricao": "Bebidas"})
        self.assertRedirects(resposta, reverse("listar_categorias"))
        self.assertTrue(Categoria.objects.filter(nome="Bebidas").exists())
        self.assertEqual(self.client.post(reverse("excluir_categoria", args=[self.categoria.pk])).status_code, 403)

    def test_formulario_rejeita_preco_negativo_e_imagem_invalida(self):
        from .forms import ProdutoForm
        data = {"nome": "Inválido", "preco": "-1.00", "descricao": "Teste", "categoria": self.categoria.pk}
        form = ProdutoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("preco", form.errors)
        data["preco"] = "10.00"
        form = ProdutoForm(data, {"imagem": SimpleUploadedFile("teste.png", b"isto nao e uma imagem", content_type="image/png")})
        self.assertFalse(form.is_valid())
        self.assertIn("imagem", form.errors)
