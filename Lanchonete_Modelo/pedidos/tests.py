from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from pessoa.models import Pessoa
from produtos.models import Categoria, Produto
from .models import Pedido, PedidoProduto


class PedidosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = Pessoa.objects.create_user(username="cliente", nome="Cliente", cpf="52998224725")
        cls.outro = Pessoa.objects.create_user(username="outro", nome="Outro", cpf="11144477735")
        cls.admin = User.objects.create_superuser(username="admin", password="AdminSeguro#2026")
        cls.categoria = Categoria.objects.create(nome="Lanches", descricao="Lanches")
        cls.produto = Produto.objects.create(nome="Lanche", preco="12.35", descricao="Lanche", categoria=cls.categoria)
        cls.bebida = Produto.objects.create(nome="Suco", preco="0.10", descricao="Suco", categoria=cls.categoria)
        cls.pedido = Pedido.objects.create(pessoa=cls.cliente)
        cls.item = PedidoProduto.objects.create(pedido=cls.pedido, produto=cls.produto, quantidade=2, preco_unitario="12.35")
        cls.pedido.recalcular_total()

    def setUp(self):
        self.client.force_login(self.cliente)

    def dados(self, itens=None, initial=0, **extras):
        if itens is None:
            itens = [{"produto": self.produto.pk, "quantidade": 2}]
        data = {"itens-TOTAL_FORMS": str(len(itens)), "itens-INITIAL_FORMS": str(initial),
                "itens-MIN_NUM_FORMS": "1", "itens-MAX_NUM_FORMS": "100"}
        for i, item in enumerate(itens):
            data.update({f"itens-{i}-{chave}": valor for chave, valor in item.items()})
        data.update(extras)
        return data

    def test_criar_pedido_com_multiplos_itens_total_e_dono_do_servidor(self):
        data = self.dados([
            {"produto": self.produto.pk, "quantidade": 2, "preco_unitario": "0.01"},
            {"produto": self.bebida.pk, "quantidade": 3},
        ], pessoa=self.outro.pk, status="Entregue", valor_total="0.01")
        resposta = self.client.post(reverse("criar_pedido"), data)
        self.assertRedirects(resposta, reverse("listar_pedidos"))
        pedido = Pedido.objects.latest("pk")
        self.assertEqual(pedido.pessoa, self.cliente)
        self.assertEqual(pedido.status, Pedido.Status.NOVO)
        self.assertEqual(pedido.valor_total, Decimal("25.00"))
        self.assertEqual(pedido.itens.count(), 2)
        self.assertEqual(pedido.produtos.count(), 2)
        self.assertEqual(pedido.itens.get(produto=self.produto).preco_unitario, Decimal("12.35"))

    def test_pedido_invalido_nao_salva_parcialmente(self):
        cenarios = [
            self.dados([]),
            self.dados([{"produto": self.produto.pk, "quantidade": 0}]),
            self.dados([{"produto": self.produto.pk, "quantidade": -1}]),
            self.dados([{"produto": self.produto.pk, "quantidade": 10001}]),
            self.dados([{"produto": self.produto.pk, "quantidade": 1}, {"produto": self.produto.pk, "quantidade": 2}]),
            self.dados([{"produto": 99999, "quantidade": 1}]),
            {},
        ]
        for data in cenarios:
            with self.subTest(data=data):
                resposta = self.client.post(reverse("criar_pedido"), data)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["formset"].errors or resposta.context["formset"].non_form_errors())
                self.assertEqual(Pedido.objects.count(), 1)
                self.assertEqual(PedidoProduto.objects.count(), 1)

    def test_produto_indisponivel_nao_pode_ser_adicionado(self):
        self.produto.disponivel = False
        self.produto.save()
        resposta = self.client.post(reverse("criar_pedido"), self.dados())
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("produto", resposta.context["formset"].errors[0])
        self.assertEqual(Pedido.objects.count(), 1)

    def test_precos_historicos_sao_preservados_na_edicao(self):
        self.produto.preco = Decimal("99.99")
        self.produto.save()
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 3}], initial=1)
        resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
        self.assertRedirects(resposta, reverse("listar_pedidos"))
        self.item.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual(self.item.preco_unitario, Decimal("12.35"))
        self.assertEqual(self.pedido.valor_total, Decimal("37.05"))

    def test_remover_item_e_adicionar_outro_recalcula_total(self):
        data = self.dados([
            {"id": self.item.pk, "produto": self.produto.pk, "quantidade": 2, "DELETE": "on"},
            {"produto": self.bebida.pk, "quantidade": 3},
        ], initial=1)
        resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
        self.assertRedirects(resposta, reverse("listar_pedidos"))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.valor_total, Decimal("0.30"))
        self.assertFalse(PedidoProduto.objects.filter(pk=self.item.pk).exists())

    def test_nao_pode_remover_todos_itens(self):
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 2, "DELETE": "on"}], initial=1)
        resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["formset"].non_form_errors())
        self.assertTrue(PedidoProduto.objects.filter(pk=self.item.pk).exists())

    def test_itens_omitidos_ou_de_outro_pedido_sao_rejeitados(self):
        outro_pedido = Pedido.objects.create(pessoa=self.outro)
        item_alheio = PedidoProduto.objects.create(pedido=outro_pedido, produto=self.bebida, quantidade=1, preco_unitario="0.10")
        cenarios = [
            self.dados(),
            self.dados([{"id": item_alheio.pk, "produto": self.bebida.pk, "quantidade": 5}], initial=1),
        ]
        for data in cenarios:
            with self.subTest(data=data):
                resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["formset"].non_form_errors() or any(resposta.context["formset"].errors))
        self.item.refresh_from_db()
        item_alheio.refresh_from_db()
        self.assertEqual(self.item.quantidade, 2)
        self.assertEqual(item_alheio.quantidade, 1)

    def test_cliente_nao_acessa_pedido_de_outro(self):
        self.client.force_login(self.outro)
        self.assertNotContains(self.client.get(reverse("listar_pedidos")), f"Pedido #{self.pedido.pk}")
        for acao in ("detalhar", "editar", "excluir"):
            self.assertEqual(self.client.get(reverse(f"{acao}_pedido", args=[self.pedido.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("excluir_pedido", args=[self.pedido.pk])).status_code, 404)
        self.assertTrue(Pedido.objects.filter(pk=self.pedido.pk).exists())

    def test_permissao_view_nao_concede_edicao(self):
        self.outro.user_permissions.add(Permission.objects.get(content_type__app_label="pedidos", codename="view_pedido"))
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(reverse("detalhar_pedido", args=[self.pedido.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("editar_pedido", args=[self.pedido.pk])).status_code, 404)

    def test_cliente_nao_altera_pedido_em_preparo(self):
        self.pedido.status = Pedido.Status.PREPARO
        self.pedido.save()
        for acao in ("editar", "excluir"):
            self.assertEqual(self.client.post(reverse(f"{acao}_pedido", args=[self.pedido.pk]), self.dados()).status_code, 403)

    def test_gestor_pode_alterar_status(self):
        self.client.force_login(self.admin)
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 2}], initial=1,
                          pessoa=self.cliente.pk, status=Pedido.Status.PREPARO)
        resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
        self.assertRedirects(resposta, reverse("listar_pedidos"))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.PREPARO)

    def test_conta_user_sem_pessoa_nao_causa_erro(self):
        user = User.objects.create_user(username="semperfil")
        self.client.force_login(user)
        self.assertRedirects(self.client.get(reverse("criar_pedido")), reverse("listar_pedidos"))
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("criar_pedido")).status_code, 200)

    def test_exclusoes_preservam_historico(self):
        for obj in (self.cliente, self.produto, self.categoria):
            with self.subTest(model=type(obj).__name__):
                with self.assertRaises(ProtectedError):
                    obj.delete()
        resposta = self.client.post(reverse("excluir_pessoa", args=[self.cliente.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "possui pedidos")
        self.assertTrue(Pedido.objects.filter(pk=self.pedido.pk).exists())
        self.client.force_login(self.admin)
        for nome, obj in [("excluir_produto", self.produto), ("excluir_categoria", self.categoria)]:
            resposta = self.client.post(reverse(nome, args=[obj.pk]))
            self.assertEqual(resposta.status_code, 200)
            self.assertContains(resposta, "está em uso")

    def test_excluir_pedido_remove_itens_e_preserva_produto(self):
        resposta = self.client.post(reverse("excluir_pedido", args=[self.pedido.pk]))
        self.assertRedirects(resposta, reverse("listar_pedidos"))
        self.assertFalse(PedidoProduto.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Produto.objects.filter(pk=self.produto.pk).exists())

    def test_constraints_impedem_quantidade_invalida_e_duplicata(self):
        for dados in [dict(quantidade=0, produto=self.bebida), dict(quantidade=1, produto=self.produto)]:
            with self.subTest(dados=dados):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    PedidoProduto.objects.create(pedido=self.pedido, preco_unitario="1.00", **dados)

    def test_admin_itens_e_total(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("admin:pedidos_pedido_add"))
        self.assertEqual(resposta.status_code, 200)
        data = self.dados(pessoa=self.cliente.pk, status=Pedido.Status.NOVO, _save="Salvar")
        resposta = self.client.post(reverse("admin:pedidos_pedido_add"), data)
        self.assertEqual(resposta.status_code, 302)
        pedido = Pedido.objects.latest("pk")
        self.assertEqual(pedido.valor_total, Decimal("24.70"))
        self.assertEqual(pedido.itens.count(), 1)

    def test_admin_rejeita_pedido_sem_itens(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(reverse("admin:pedidos_pedido_add"), self.dados(
            [], pessoa=self.cliente.pk, status=Pedido.Status.NOVO, _save="Salvar"
        ))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 1)

    def test_management_form_e_ids_adulterados_nao_modificam_itens(self):
        original = {"id": self.item.pk, "produto": self.produto.pk, "quantidade": 3}
        cenarios = [
            self.dados([original], initial=0),
            self.dados([original, dict(original, DELETE="on")], initial=2),
            self.dados([dict(original, DELETE="on"), original], initial=2),
            self.dados([original, dict(original, produto=self.bebida.pk)], initial=1),
        ]
        for data in cenarios:
            with self.subTest(data=data):
                resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["formset"].non_form_errors())
                self.item.refresh_from_db()
                self.pedido.refresh_from_db()
                self.assertEqual(self.item.quantidade, 2)
                self.assertEqual(self.pedido.valor_total, Decimal("24.70"))
                self.assertEqual(self.pedido.itens.count(), 1)

    def test_falha_ao_salvar_itens_reverte_pedido_e_edicao(self):
        for nome, args, data in [
            ("criar_pedido", [], self.dados()),
            ("editar_pedido", [self.pedido.pk], self.dados([
                {"id": self.item.pk, "produto": self.produto.pk, "quantidade": 3},
            ], initial=1)),
        ]:
            with self.subTest(nome=nome):
                with patch("pedidos.views.PedidoProdutoFormSet.save", side_effect=RuntimeError("Falha simulada")):
                    with self.assertRaisesMessage(RuntimeError, "Falha simulada"):
                        self.client.post(reverse(nome, args=args), data)
                self.assertEqual(Pedido.objects.count(), 1)
                self.item.refresh_from_db()
                self.pedido.refresh_from_db()
                self.assertEqual(self.item.quantidade, 2)
                self.assertEqual(self.pedido.valor_total, Decimal("24.70"))

    def test_permissoes_administrativas_por_acao(self):
        self.client.force_login(self.outro)
        self.outro.user_permissions.add(Permission.objects.get(content_type__app_label="pedidos", codename="add_pedido"))
        resposta = self.client.post(reverse("criar_pedido"), self.dados(pessoa=self.cliente.pk, status=Pedido.Status.PREPARO))
        self.assertEqual(resposta.status_code, 302)
        criado = Pedido.objects.latest("pk")
        self.assertEqual(criado.pessoa_id, self.cliente.pk)
        self.assertEqual(criado.status, Pedido.Status.PREPARO)
        self.assertEqual(self.client.get(reverse("detalhar_pedido", args=[criado.pk])).status_code, 404)
        self.outro.user_permissions.set([Permission.objects.get(content_type__app_label="pedidos", codename="change_pedido")])
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 4}], initial=1,
                          pessoa=self.cliente.pk, status=Pedido.Status.ENTREGUE)
        self.assertEqual(self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data).status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.Status.ENTREGUE)
        self.assertEqual(self.pedido.valor_total, Decimal("49.40"))
        self.assertEqual(self.client.post(reverse("excluir_pedido", args=[self.pedido.pk])).status_code, 404)
        self.outro.user_permissions.set([Permission.objects.get(content_type__app_label="pedidos", codename="delete_pedido")])
        self.assertEqual(self.client.post(reverse("excluir_pedido", args=[self.pedido.pk])).status_code, 302)
        self.assertFalse(Pedido.objects.filter(pk=self.pedido.pk).exists())

    def test_todos_status_nao_novos_bloqueiam_cliente_e_ocultam_acoes(self):
        for status in Pedido.Status.values:
            if status == Pedido.Status.NOVO:
                continue
            self.pedido.status = status
            self.pedido.save()
            pagina = self.client.get(reverse("detalhar_pedido", args=[self.pedido.pk]))
            self.assertContains(pagina, self.produto.nome)
            for acao in ("editar", "excluir"):
                url = reverse(f"{acao}_pedido", args=[self.pedido.pk])
                self.assertNotContains(pagina, url)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, self.dados()).status_code, 403)

    def test_post_edicao_de_outro_pedido_nao_altera_dados(self):
        self.client.force_login(self.outro)
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 9}], initial=1)
        self.assertEqual(self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data).status_code, 404)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, 2)

    def test_produto_indisponivel_permite_reducao_mas_nao_aumento(self):
        self.produto.disponivel = False
        self.produto.save()
        data = self.dados([{"id": self.item.pk, "produto": self.produto.pk, "quantidade": 3}], initial=1)
        resposta = self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("produto", resposta.context["formset"].errors[0])
        data["itens-0-quantidade"] = 1
        self.assertEqual(self.client.post(reverse("editar_pedido", args=[self.pedido.pk]), data).status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.valor_total, Decimal("12.35"))

    def test_total_acima_do_limite_nao_salva(self):
        self.produto.preco = Decimal("9999999999.99")
        self.produto.save()
        resposta = self.client.post(reverse("criar_pedido"), self.dados())
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["formset"].non_form_errors())
        self.assertEqual(Pedido.objects.count(), 1)
