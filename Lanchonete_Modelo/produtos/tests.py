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

    def test_metodos_http_objetos_inexistentes_e_get_sem_exclusao(self):
        self.client.force_login(self.pessoa)
        for singular, plural, objeto in (
            ("categoria", "categorias", self.categoria), ("produto", "produtos", self.produto),
            ("pessoa", "pessoas", self.pessoa), ("pedido", "pedidos", self.pedido),
        ):
            for nome, args in [(f"listar_{plural}", []), (f"detalhar_{singular}", [objeto.pk])]:
                with self.subTest(nome=nome):
                    self.assertEqual(self.client.head(reverse(nome, args=args)).status_code, 200)
                    self.assertEqual(self.client.post(reverse(nome, args=args)).status_code, 405)
            for acao in ("criar", "editar", "excluir"):
                args = [] if acao == "criar" else [objeto.pk]
                url = reverse(f"{acao}_{singular}", args=args)
                self.assertEqual(self.client.get(url).status_code, 200)
                for metodo in (self.client.put, self.client.patch, self.client.delete):
                    self.assertEqual(metodo(url).status_code, 405)
                self.assertTrue(type(objeto).objects.filter(pk=objeto.pk).exists())
            for acao in ("detalhar", "editar", "excluir"):
                self.assertEqual(self.client.get(reverse(f"{acao}_{singular}", args=[99999])).status_code, 404)
        self.assertEqual(self.client.post(reverse("minha_conta")).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.put(reverse("cadastro")).status_code, 405)

    def test_rotas_protegidas_redirecionam_anonimo_para_login(self):
        rotas = [("minha_conta", []), ("alterar_senha", []), ("senha_alterada", [])]
        for singular, plural, objeto in (
            ("categoria", "categorias", self.categoria), ("produto", "produtos", self.produto),
            ("pessoa", "pessoas", self.pessoa), ("pedido", "pedidos", self.pedido),
        ):
            rotas.extend((f"{acao}_{singular}", [] if acao == "criar" else [objeto.pk])
                         for acao in ("criar", "editar", "excluir"))
            if singular in ("pessoa", "pedido"):
                rotas.extend([(f"listar_{plural}", []), (f"detalhar_{singular}", [objeto.pk])])
        for nome, args in rotas:
            with self.subTest(nome=nome):
                url = reverse(nome, args=args)
                self.assertRedirects(self.client.get(url), f"{reverse('login_pessoa')}?next={url}")


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

    def test_catalogo_publico_sem_acoes_administrativas(self):
        for model, plural, objeto in [("categoria", "categorias", self.categoria), ("produto", "produtos", self.produto)]:
            lista = self.client.get(reverse(f"listar_{plural}"))
            self.assertContains(lista, objeto.nome)
            self.assertNotContains(lista, reverse(f"criar_{model}"))
            detalhe = self.client.get(reverse(f"detalhar_{model}", args=[objeto.pk]))
            self.assertContains(detalhe, objeto.descricao)
            for acao in ("editar", "excluir"):
                self.assertNotContains(detalhe, reverse(f"{acao}_{model}", args=[objeto.pk]))

    def test_crud_com_permissoes_individuais_e_feedback(self):
        from django.contrib.auth.models import Permission
        for model, classe, plural in [("categoria", Categoria, "categorias"), ("produto", Produto, "produtos")]:
            data = {"nome": "Novo", "descricao": "Descrição"}
            if model == "produto":
                data.update(preco="10.00", categoria=self.categoria.pk)
            for acao, codename in [("criar", "add"), ("editar", "change"), ("excluir", "delete")]:
                with self.subTest(model=model, acao=acao):
                    self.cliente.user_permissions.set([Permission.objects.get(
                        content_type__app_label="produtos", codename=f"{codename}_{model}"
                    )])
                    self.client.force_login(self.cliente)
                    args = [] if acao == "criar" else [objeto.pk]
                    if acao == "editar":
                        data["nome"] = "Atualizado"
                    resposta = self.client.post(reverse(f"{acao}_{model}", args=args), data, follow=True)
                    self.assertEqual(resposta.status_code, 200)
                    self.assertContains(resposta, "sucesso")
                    if acao == "criar":
                        objeto = classe.objects.get(nome="Novo")
                    elif acao == "editar":
                        objeto.refresh_from_db()
                        self.assertEqual(objeto.nome, "Atualizado")
                    else:
                        self.assertFalse(classe.objects.filter(pk=objeto.pk).exists())
                    outro_codename = "change" if codename == "add" else "add"
                    outra_acao = "editar" if outro_codename == "change" else "criar"
                    outros_args = [objeto.pk] if outra_acao == "editar" else []
                    self.assertEqual(self.client.post(reverse(f"{outra_acao}_{model}", args=outros_args)).status_code, 403)

    def test_formularios_invalidos_exibem_erros_sem_salvar(self):
        from django.contrib.auth.models import Permission
        self.cliente.user_permissions.set(Permission.objects.filter(content_type__app_label="produtos"))
        self.client.force_login(self.cliente)
        for model, objeto in [("categoria", self.categoria), ("produto", self.produto)]:
            for acao in ("criar", "editar"):
                args = [] if acao == "criar" else [objeto.pk]
                resposta = self.client.post(reverse(f"{acao}_{model}", args=args), {})
                self.assertEqual(resposta.status_code, 200)
                self.assertIn("nome", resposta.context["form"].errors)
                self.assertContains(resposta, "invalid-feedback")
            objeto.refresh_from_db()
            self.assertEqual(type(objeto).objects.count(), 1)
