# Lanchonete Modelo

Projeto acadêmico de Programação de Sistemas Web II com Django, SQLite e autenticação
por `django.contrib.auth`. Implementa exatamente quatro CRUDs: **Categoria, Produto,
Pessoa e Pedido**, com criação, listagem, detalhe, edição e exclusão.
PedidoProduto representa os itens de Pedido e não possui CRUD independente.

## Instalação e execução

Requisitos: Python 3.12 ou superior e pip. Execute a partir da pasta deste README.

```bash
python -m venv .venv
```

Ative o ambiente no Windows/PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Windows/cmd, use `.venv\Scripts\activate.bat`. No Linux/macOS, use
`source .venv/bin/activate`. Depois:

```bash
python -m pip install -r requirements.txt
cd Lanchonete_Modelo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://127.0.0.1:8000/. Se já possui ambiente e banco configurados, ative o
ambiente, aplique as migrations pendentes e inicie o servidor. Não é necessário
criar outro superusuário. Não apague o banco nem as migrations para atualizar.
O requirements.txt utiliza UTF-8 sem BOM e fixa as dependências do projeto.

## Organização

```text
Lanchonete_Modelo/
├── manage.py
├── lanchonete/       # Configurações, URLs, ASGI e WSGI
├── pessoa/           # Herança de User, cadastro, perfil e autenticação
├── produtos/         # Categoria e Produto
├── pedidos/          # Pedido e seus itens
├── templates/        # Layout compartilhado
└── static/           # CSS e JavaScript
 diagrama/           # Diagrama UML original (na raiz do repositório)
 requirements.txt    # Dependências (na raiz do repositório)
```

Cada aplicação mantém models, forms, views, URLs, admin, migrations, templates e
 testes. As views da aplicação são Function-Based Views; login/logout e troca de
senha usam as views fornecidas pelo Django. O banco local fica em
`Lanchonete_Modelo/db.sqlite3`; imagens ficam em `Lanchonete_Modelo/media/`.
Não versione esses dados. O banco e alguns caches já estavam versionados;
`.gitignore` não os retira automaticamente do histórico.

## Diagrama e relacionamentos

A referência do domínio é o [diagrama UML original](diagrama/DIAGRAMA%20UML%20PSWatualizado.drawio.png).

- Pessoa especializa User por herança multitable e possui nome e CPF.
- Uma Pessoa possui vários Pedidos; cada Pedido pertence a uma Pessoa.
- Uma Categoria possui vários Produtos; cada Produto pertence a uma Categoria.
- Pedido e Produto têm relação muitos-para-muitos através de PedidoProduto,
  que armazena quantidade e preço unitário histórico.

Os tipos existentes preservam CPF como texto (inclusive zeros iniciais), valores
monetários como Decimal e data do pedido com horário. São representações técnicas
dos atributos do UML, sem novas entidades ou alteração dos relacionamentos.
Categoria com produtos, Produto utilizado em itens e Pessoa com pedidos têm exclusão
protegida. Excluir Pedido remove seus itens e preserva os produtos.

## Cadastro, login e permissões

- **Cliente:** use Cadastre-se ou `/pessoas/cadastro/`. Informe nome, CPF válido,
  usuário, senha e, opcionalmente, e-mail. Depois entre em `/pessoas/login/`.
- **Minha conta:** permite consultar, editar e excluir o próprio perfil, respeitando
  a proteção de exclusão por pedidos. A troca de senha autenticada está disponível.
- **Categoria e Produto:** listagem e detalhe públicos. Criar, editar e excluir
  exigem login e, respectivamente, add, change e delete do model no app produtos.
- **Pessoa:** listar exige pessoa.view_pessoa; criar administrativamente exige
  pessoa.add_pessoa. Consultar, editar e excluir terceiros exigem a permissão da
  ação. Apenas superusuários podem alterar ou excluir contas de outros usuários
  que sejam staff/superuser pelas views de Pessoa.
- **Pedido:** exige login. Sem a permissão da ação em pedidos, o usuário acessa
  somente seus pedidos; edição e exclusão pelo cliente exigem status Novo.
  view_pedido, add_pedido, change_pedido e delete_pedido concedem acesso
  administrativo para suas respectivas operações; uma não concede as demais.
  Usuários sem Pessoa precisam de add_pedido para cadastrar para um cliente.
- **Administração:** o superusuário acessa `/admin/` e atribui permissões diretamente
  ou por grupos. createsuperuser cria um User administrativo, sem criar Pessoa
  automaticamente. is_staff permite entrar no admin, mas não substitui permissões.
  Para gerenciar itens no admin, atribua as permissões necessárias de PedidoProduto;
  os itens continuam dentro de Pedido. A administração de credenciais e privilégios
  de Pessoa no admin é exclusiva do superusuário.

Não há senha padrão. Cadastro público não atribui privilégios. Login respeita o
 destino local next; páginas protegidas redirecionam visitantes para login.
Sair exige POST com CSRF: use o botão Sair. Recuperação de senha por e-mail não está
implementada; o superusuário pode redefinir senhas no admin.

Exclusões são confirmadas por GET e executadas somente por POST com CSRF. Os itens
são validados e salvos junto ao Pedido em transação; o total é recalculado no servidor.
Produtos repetidos, quantidades inválidas, IDs adulterados e pedidos sem itens são
rejeitados. O preço histórico é preservado na edição; produtos indisponíveis não
aceitam novas unidades. Cada item aceita até 10000 unidades, com até 100 itens.

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

## Testes e verificações

Execute dentro de `Lanchonete_Modelo/`:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m pip check
```

A suíte cobre os quatro CRUDs, permissões individuais e por grupos, acesso a dados
de terceiros, staff/superuser, login/logout, CSRF, imagens, exclusões protegidas,
métodos HTTP, status, itens, totais e rollback transacional. Os testes usam banco
isolado; uploads de teste usam diretório temporário do sistema operacional.

## Configuração de ambiente

Por padrão o projeto funciona em desenvolvimento local. As variáveis são lidas do
ambiente do processo; arquivos `.env` não são carregados automaticamente.

| Variável | Uso |
| --- | --- |
| `DJANGO_DEBUG` | `true` por padrão; use `false` ao publicar |
| `DJANGO_SECRET_KEY` | Chave externa obrigatória com debug desativado |
| `DJANGO_ALLOWED_HOSTS` | Hosts separados por vírgula; padrão `localhost,127.0.0.1,[::1]` |

Com debug desativado, cookies seguros, redirecionamento HTTPS e HSTS são habilitados.
A publicação precisa de domínio, HTTPS, servidor WSGI/ASGI e serviço próprio para
estáticos e mídia. Execute collectstatic e check --deploy no ambiente de publicação.
O runserver serve apenas ao desenvolvimento.
