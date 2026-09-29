from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import PessoaCadastroForm
from .models import Pessoa


SENHA = "CadastroSeguro#2026"


class CadastroAuthTests(TestCase):
    def dados(self, **kwargs):
        data = {"username": "cliente", "nome": "Cliente", "cpf": "529.982.247-25",
                "email": "cliente@example.com", "password1": SENHA, "password2": SENHA}
        data.update(kwargs)
        return data

    def test_cadastro_cria_user_pessoa_e_senha_protegida_sem_privilegios(self):
        resposta = self.client.post(reverse("cadastro"), self.dados(is_staff="on", is_superuser="on"))
        self.assertRedirects(resposta, reverse("login_pessoa"))
        pessoa = Pessoa.objects.get(username="cliente")
        self.assertEqual(pessoa.cpf, "52998224725")
        self.assertEqual(User.objects.get(pk=pessoa.pk).username, "cliente")
        self.assertNotEqual(pessoa.password, SENHA)
        self.assertTrue(pessoa.check_password(SENHA))
        self.assertFalse(pessoa.is_staff)
        self.assertFalse(pessoa.is_superuser)
        self.assertFalse(pessoa.groups.exists())
        self.assertFalse(pessoa.user_permissions.exists())
        self.assertEqual(authenticate(username="cliente", password=SENHA).pk, pessoa.pk)
        self.assertRedirects(self.client.post(reverse("cadastro"), self.dados(
            username="segundo", cpf="11144477735"
        )), reverse("login_pessoa"))
        self.assertEqual(Pessoa.objects.count(), 2)

    def test_cadastro_rejeita_dados_invalidos(self):
        for mudanca, campo in [
            ({"password2": "diferente"}, "password2"),
            ({"password1": "123", "password2": "123"}, "password2"),
            ({"cpf": "11111111111"}, "cpf"),
            ({"cpf": "52998224724"}, "cpf"),
            ({"cpf": "abc52998224725"}, "cpf"),
            ({"cpf": "123"}, "cpf"),
            ({"email": "invalido"}, "email"),
        ]:
            with self.subTest(mudanca=mudanca):
                form = PessoaCadastroForm(data=self.dados(**mudanca))
                self.assertFalse(form.is_valid())
                self.assertIn(campo, form.errors)
        self.assertEqual(User.objects.count(), 0)
        self.assertFalse(self.client.post(reverse("cadastro"), {}).context["form"].is_valid())

    def test_username_de_admin_e_cpf_duplicados(self):
        User.objects.create_user(username="Admin", password=SENHA)
        form = PessoaCadastroForm(data=self.dados(username="admin"))
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.client.post(reverse("cadastro"), self.dados())
        form = PessoaCadastroForm(data=self.dados(username="outro", cpf="52998224725"))
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_login_next_local_e_bloqueio_de_redirecionamento_externo(self):
        self.client.post(reverse("cadastro"), self.dados())
        for destino, esperado in [("/pedidos/", "/pedidos/"), ("https://externo.example/", "/produtos/")]:
            with self.subTest(destino=destino):
                self.client.logout()
                resposta = self.client.post(reverse("login_pessoa"), {
                    "username": "cliente", "password": SENHA, "next": destino,
                })
                self.assertRedirects(resposta, esperado)

    def test_usuario_inativo_e_senha_incorreta_nao_entram(self):
        user = User.objects.create_user(username="cliente", password=SENHA)
        for ativa, senha in [(True, "errada"), (False, SENHA)]:
            user.is_active = ativa
            user.save()
            resposta = self.client.post(reverse("login_pessoa"), {"username": user.username, "password": senha})
            self.assertEqual(resposta.status_code, 200)
            self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_exige_post_e_csrf(self):
        user = User.objects.create_user(username="cliente", password=SENHA)
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(user)
        self.assertEqual(cliente.get(reverse("logout_pessoa")).status_code, 405)
        self.assertEqual(cliente.post(reverse("logout_pessoa")).status_code, 403)
        cliente.get(reverse("listar_produtos"))
        resposta = cliente.post(reverse("logout_pessoa"), {"csrfmiddlewaretoken": cliente.cookies["csrftoken"].value})
        self.assertRedirects(resposta, reverse("login_pessoa"))
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_cadastro_exige_csrf(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse("cadastro"), self.dados()).status_code, 403)
        self.assertFalse(Pessoa.objects.exists())

    def test_alteracao_de_senha_preserva_sessao(self):
        user = User.objects.create_user(username="cliente", password=SENHA)
        self.client.force_login(user)
        nova = "OutraSenhaSegura#2026"
        resposta = self.client.post(reverse("alterar_senha"), {
            "old_password": SENHA, "new_password1": nova, "new_password2": nova,
        })
        self.assertRedirects(resposta, reverse("senha_alterada"))
        user.refresh_from_db()
        self.assertTrue(user.check_password(nova))
        self.assertIn("_auth_user_id", self.client.session)


class PessoaPermissoesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pessoa = Pessoa.objects.create_user(username="cliente", password=SENHA, nome="Cliente", cpf="52998224725")
        cls.outra = Pessoa.objects.create_user(username="outra", password=SENHA, nome="Outra", cpf="11144477735")

    def test_visitante_nao_acessa_pessoas(self):
        for nome, args in [("listar_pessoas", []), ("criar_pessoa", []), ("detalhar_pessoa", [self.pessoa.pk]),
                           ("editar_pessoa", [self.pessoa.pk]), ("excluir_pessoa", [self.pessoa.pk])]:
            with self.subTest(nome=nome):
                self.assertEqual(self.client.get(reverse(nome, args=args)).status_code, 302)

    def test_cliente_acessa_somente_o_proprio_perfil(self):
        self.client.force_login(self.pessoa)
        self.assertEqual(self.client.get(reverse("listar_pessoas")).status_code, 403)
        self.assertEqual(self.client.get(reverse("criar_pessoa")).status_code, 403)
        for acao in ("detalhar", "editar", "excluir"):
            self.assertEqual(self.client.get(reverse(f"{acao}_pessoa", args=[self.outra.pk])).status_code, 403)
            self.assertEqual(self.client.get(reverse(f"{acao}_pessoa", args=[self.pessoa.pk])).status_code, 200)

    def test_edicao_nao_altera_senha_ou_privilegios(self):
        self.client.force_login(self.pessoa)
        senha = self.pessoa.password
        resposta = self.client.post(reverse("editar_pessoa", args=[self.pessoa.pk]), {
            "nome": "Atualizado", "cpf": self.pessoa.cpf, "email": "novo@example.com",
            "password": "texto-puro", "username": "invadido", "is_superuser": "on", "is_staff": "on",
        })
        self.assertEqual(resposta.status_code, 302)
        self.pessoa.refresh_from_db()
        self.assertEqual(self.pessoa.nome, "Atualizado")
        self.assertEqual(self.pessoa.password, senha)
        self.assertEqual(self.pessoa.username, "cliente")
        self.assertFalse(self.pessoa.is_superuser)
        self.assertFalse(self.pessoa.is_staff)

    def test_permissao_via_grupo_e_respeitada(self):
        grupo = Group.objects.create(name="Consulta de pessoas")
        grupo.permissions.add(Permission.objects.get(content_type__app_label="pessoa", codename="view_pessoa"))
        self.pessoa.groups.add(grupo)
        self.client.force_login(self.pessoa)
        self.assertEqual(self.client.get(reverse("listar_pessoas")).status_code, 200)
        self.assertEqual(self.client.get(reverse("detalhar_pessoa", args=[self.outra.pk])).status_code, 200)
        self.assertEqual(self.client.post(reverse("excluir_pessoa", args=[self.outra.pk])).status_code, 403)

    def test_exclusao_propria_apaga_user_e_encerra_sessao(self):
        self.client.force_login(self.pessoa)
        resposta = self.client.post(reverse("excluir_pessoa", args=[self.pessoa.pk]))
        self.assertRedirects(resposta, reverse("listar_produtos"))
        self.assertFalse(User.objects.filter(pk=self.pessoa.pk).exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_cria_pessoa_com_hash_e_edita_sem_corromper_senha(self):
        admin = User.objects.create_superuser(username="admin", password=SENHA)
        self.client.force_login(admin)
        resposta = self.client.post(reverse("admin:pessoa_pessoa_add"), {
            "username": "novo", "nome": "Novo", "cpf": "01234567890",
            "password1": SENHA, "password2": SENHA, "_save": "Salvar",
        })
        self.assertEqual(resposta.status_code, 302)
        pessoa = Pessoa.objects.get(username="novo")
        self.assertTrue(pessoa.check_password(SENHA))
        resposta = self.client.get(reverse("admin:pessoa_pessoa_change", args=[pessoa.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, SENHA)

    def test_permissao_change_pessoa_nao_libera_flags_no_admin(self):
        self.pessoa.is_staff = True
        self.pessoa.save()
        self.pessoa.user_permissions.add(Permission.objects.get(content_type__app_label="pessoa", codename="change_pessoa"))
        self.client.force_login(self.pessoa)
        self.assertEqual(self.client.get(reverse("admin:pessoa_pessoa_change", args=[self.outra.pk])).status_code, 403)
