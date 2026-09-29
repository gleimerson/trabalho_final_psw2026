# Integração do Baker 1.0.0

O projeto usa o Baker 1.0.0 (HTML Codex) como camada visual, mantendo as rotas, views, permissões, formulários e modelos da Lanchonete Modelo. O template fornece Bootstrap 5.0.0, imagens, estilos e componentes de navegação; o conteúdo foi traduzido e substituído por dados do projeto.

## Organização

- Os arquivos do template ficam em `Lanchonete_Modelo/static/baker/`, separados em `css/`, `img/`, `js/`, `lib/`, `fonts/` e `webfonts/`.
- `templates/base.html` carrega os estilos na ordem do Baker e o `static/css/site.css` por último. `includes/` contém navbar, mensagens, rodapé, cartões e imagens de produtos.
- `form_base.html` e `confirmar_exclusao_base.html` padronizam formulários e exclusões. `produtos/templatetags/form_ui.py` adapta widgets para Bootstrap 5 sem alterar validação.
- `static/js/app.js` inicializa apenas plugins disponíveis, remove o spinner, trata o botão de topo e mantém o fallback de imagens.

Os assets são servidos em desenvolvimento por `STATIC_URL` e, em produção, devem ser reunidos com `python manage.py collectstatic`. Uploads continuam em `MEDIA_ROOT` e são servidos por `MEDIA_URL` somente quando `DEBUG` está ativo.

Quando um produto não possui imagem, o cartão usa `baker/img/product-1.jpg` como imagem padrão. O template Baker anterior não usado pelo projeto não foi copiado; também não foram copiados SCSS, HTMLs de exemplo, o preview e dependências não utilizadas.

O crédito do template foi removido do rodapé a pedido do responsável pelo projeto.

## Verificações

- `python manage.py check`: passou sem erros.
- `python manage.py makemigrations --check --dry-run`: passou, sem mudanças detectadas.
- `python manage.py collectstatic --noinput --dry-run`: passou; 173 arquivos encontrados, sem avisos de arquivo ausente.
- `python manage.py test`: 40 testes passaram.
- Cliente Django: início (302 para produtos), produtos, categorias, login, cadastro, pedidos, pessoas e páginas de detalhe/formulário responderam conforme as permissões (200, 302 ou 403).

## Entrega

Criados ou alterados: `static/baker/`, `static/css/site.css`, `static/js/app.js`, `templates/base.html`, `templates/includes/`, `templates/form_base.html`, `templates/confirmar_exclusao_base.html`, `templates/403.html`, `templates/404.html`, templates de pessoas, produtos, categorias e pedidos, `produtos/templatetags/form_ui.py` e este documento. Não foram alterados rotas, views, forms, models ou migrations, nem removidos testes. A home existente continua redirecionando para a listagem de produtos; o hero Baker aparece nessa listagem, pois essa era a regra atual do projeto.
