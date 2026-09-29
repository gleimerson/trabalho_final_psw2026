# Lanchonete Modelo

Projeto acadêmico de Programação de Sistemas Web com Django 6, SQLite e autenticação
por `django.contrib.auth`. Gerencia pessoas, categorias, produtos e pedidos com itens.

## Executar localmente

Requisitos: Python 3.12 ou superior e pip. A partir desta pasta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd Lanchonete_Modelo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://127.0.0.1:8000/. No Windows, ative o ambiente com `.venv\Scripts\activate`.
Se já possui ambiente e banco configurados, basta ativar o ambiente, aplicar novas
migrações e iniciar o servidor. Não é necessário criar outro superusuário.

## Cadastro e acesso

- **Cliente:** use **Cadastre-se** ou `/pessoas/cadastro/`. Informe nome, CPF válido,
  usuário, senha e, opcionalmente, e-mail. Depois entre em `/pessoas/login/`.
- **Minha conta:** permite consultar e editar o próprio perfil e alterar a senha.
- **Pedidos:** o cliente escolhe produtos e quantidades. O servidor calcula o total.
  Cada cliente consulta apenas seus pedidos e pode editar ou excluir os que estão em `Novo`.
- **Administração:** o superusuário acessa `/admin/`, gerencia cadastros e atribui
  permissões diretamente aos usuários ou por grupos. `createsuperuser` cria um `User`
  administrativo; não cria automaticamente uma `Pessoa` com CPF.
- **Funcionários:** configure grupos no admin com as permissões necessárias de
  `pessoa`, `produtos` e `pedidos`. `is_staff` permite acessar o admin, mas não substitui
  essas permissões. Para editar itens no admin, inclua as permissões de `PedidoProduto`.
  A administração de credenciais e privilégios de `Pessoa` no admin é exclusiva do superusuário.

Não há senha padrão. O cadastro público não atribui permissões administrativas.
Sair exige POST com CSRF; use o botão **Sair**. Recuperação de senha por e-mail não está
implementada; a troca de senha autenticada está disponível e o superusuário pode redefinir
senhas no admin.

## Organização

```text
Lanchonete_Modelo/
├── manage.py
├── lanchonete/       # Configurações, URLs, ASGI e WSGI
├── pessoa/           # Herança de User, cadastro, perfil e autenticação
├── produtos/         # Produtos e categorias
├── pedidos/          # Pedidos, itens, total e permissões
├── templates/        # Layout compartilhado
└── static/           # CSS e JavaScript
diagrama/            # Diagrama original do projeto
docs/revisao.md      # Comparação com o diagrama e revisão técnica
requirements.txt     # Dependências
```

Cada aplicação mantém modelos, formulários, views, URLs, admin, migrations, templates e testes.
O banco local fica em `Lanchonete_Modelo/db.sqlite3`; imagens ficam em
`Lanchonete_Modelo/media/`. Backups locais ficam em `backups/`. Não versione esses dados.
O banco e alguns caches já estavam versionados anteriormente; `.gitignore` não os retira
automaticamente do histórico.

## Rotas principais

| Área | Endereço |
| --- | --- |
| Produtos | `/produtos/` |
| Categorias | `/produtos/categorias/` |
| Cadastro público | `/pessoas/cadastro/` |
| Login | `/pessoas/login/` |
| Minha conta | `/pessoas/minha-conta/` |
| Troca de senha | `/pessoas/senha/` |
| Pessoas (exige permissão) | `/pessoas/` |
| Pedidos | `/pedidos/` |
| Administração | `/admin/` |

Os endereços antigos com prefixos duplicados continuam aceitos, com as mesmas permissões.

## Verificações

Execute **dentro de `Lanchonete_Modelo/`**, para que a descoberta de testes encontre as aplicações:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python -m pip check
```

Os testes usam banco temporário e os testes de upload usam pasta temporária.
Não exclua o banco nem as migrations para aplicar uma atualização.

## Configuração de ambiente

Por padrão o projeto funciona em desenvolvimento local. As variáveis são lidas do
ambiente do processo; arquivos `.env` não são carregados automaticamente.

| Variável | Uso |
| --- | --- |
| `DJANGO_DEBUG` | `true` por padrão; use `false` ao publicar |
| `DJANGO_SECRET_KEY` | Chave externa obrigatória com debug desativado |
| `DJANGO_ALLOWED_HOSTS` | Hosts separados por vírgula; padrão `localhost,127.0.0.1,[::1]` |

Com debug desativado, cookies seguros, redirecionamento HTTPS e HSTS são habilitados.
A publicação ainda precisa de domínio, HTTPS, servidor WSGI/ASGI e serviço próprio para
estáticos e mídia. Execute `collectstatic` e `check --deploy` com o ambiente de publicação.
O `runserver` serve apenas ao desenvolvimento.

Veja [a revisão técnica e a comparação com o diagrama](docs/revisao.md).
