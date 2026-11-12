# Aplicar a nova interface (TailAdmin) nos templates Django

- Status: em andamento
- Critérios: T3-2.5 (reforço); preservar DEF-4, DEF-7, T1-1.5, T2-1.4, T2-2.3, T3-1.2, T3-1.4, T3-1.5, T3-2.3c
- Entrada: aplicar nos templates o visual do `docs/design/DESIGN.md` e do protótipo https://claude.ai/artifact/Qo296wGA8fiFjxLpa6wzMJ

## Contexto

O DESIGN.md reescrito e o protótipo clicável com todas as telas estão na branch `docs/design-tailadmin` (ainda sem merge). O sistema publicado ainda usa o visual antigo. A identidade antiga era o azul-petróleo com Manrope/IBM Plex, sem ícones, com tabelas que não se adaptam ao celular.

Este plano leva a proposta para o Django sem trocar de framework. O Bootstrap 5 continua: os tokens do TailAdmin sobrescrevem as variáveis `--bs-*`, as fontes passam a ser Outfit e os ícones, o Bootstrap Icons.

O comportamento não muda. Continuam iguais:

- views, permissões e regras de negócio;
- as URLs;
- jQuery, Bootbox, jQuery Mask e a templatetag `url_pagina`.

Muda só a apresentação. Há duas exceções pequenas que alimentam a tela:

- o progresso dos projetos no painel;
- a indicação de prazo vencido no quadro.

Fica de fora: o seletor "ver como" do protótipo. Ele só existe para a demonstração; no sistema, o papel vem do login.

## 1. Revisão de configurações e ambiente

- [x] Branch de partida: `docs/design-tailadmin`, que tem o DESIGN.md e o protótipo. A implementação vai em `feat/interface-tailadmin`, criada a partir dela.
- [x] CDNs já usados: Bootstrap 5.3.3, jQuery 3.7.1, Bootbox 6.0.0 e Mask 1.14.16 no jsDelivr. Entram mais dois na mesma linha:
  - Bootstrap Icons 1.11.3 (jsDelivr);
  - Outfit (Google Fonts).

  Nenhum pacote Python novo.
- [x] Marcações que os testes verificam e que **não podem mudar** de nome:
  - `<p class="board-empty">Nenhuma tarefa</p>`;
  - "Este projeto ainda não tem tarefas" e "Peça ao gerente";
  - `data-excluir` e `data-sugestao`;
  - os ids do assistente: `#mensagens`, `#pergunta`, `#form-assistente`, `#cota-barra` e `#cota-texto`;
  - os links de paginação com `title=…&priority=…&page=N`;
  - o template `registration/login.html` e o "Criar conta".
- [ ] Religar o PostgreSQL descartável (porta 54329) e o banco `naes_demo` com o `popular_demo`, para a verificação visual local.

## 2. Etapas e commits

### A. Base visual
- [ ] `docs(plans): planejar a aplicação da nova interface`. Salva este plano em `docs/plans/2026-11-12-aplicar-interface-tailadmin.md`.
- [ ] `feat(ui): tokens do TailAdmin, Outfit e Bootstrap Icons`
  - `static/css/theme.css` reescrito com os tokens da seção 3.2 do DESIGN.md. O Bootstrap 5.3 usa `data-bs-theme` no `<html>`, então os seletores são `:root`/`[data-bs-theme="light"]` e `[data-bs-theme="dark"]`.
  - Mapeamento para o Bootstrap:
    - `--bs-body-bg`, `--bs-body-color`, `--bs-border-color`, `--bs-secondary-color`;
    - `--bs-primary` e `--bs-primary-rgb`;
    - `--bs-body-font-family` (Outfit);
    - `--bs-border-radius` de 8px e `--bs-border-radius-lg` de 16px.
  - Ajuste das classes do Bootstrap ao novo visual:
    - botões `.btn-primary`, `.btn-outline-secondary` e `.btn-outline-danger`;
    - `.form-control` e `.form-select`, com 44px e anel de foco;
    - `.card`, `.table`, `.dropdown-menu` e `.toast`.
  - `templates/base.html`:
    - carrega a fonte Outfit e o Bootstrap Icons;
    - script inline que aplica o tema salvo no `localStorage` ou o `prefers-color-scheme`;
    - link "Pular para o conteúdo";
    - `{% block trilha %}` para a trilha de navegação.
- [ ] `feat(ui): templatetags e parciais da interface`
  - `pages/templatetags/ui.py` concentra o mapeamento da seção 3.3 do DESIGN.md num só lugar:
    - `{% icone "kanban" %}`;
    - `{% etiqueta_prioridade tarefa %}`, `{% etiqueta_estagio estagio %}`, `{% etiqueta_papel usuario %}` e `{% etiqueta_situacao chamada %}`;
    - o filtro `iniciais`.
  - Parciais em `templates/includes/`:
    - `page_head.html`, com título, descrição e bloco de ações;
    - `empty_state.html`, com ícone, título, texto e ação opcional.

### B. Estrutura e componentes compartilhados
- [ ] `feat(ui): barra lateral com ícones e cabeçalho com menu do usuário`
  - `includes/sidebar.html`:
    - ícones da seção 10 do DESIGN.md e grupos em maiúsculas;
    - o mesmo controle por `request.user.is_authenticated` e por papel (T2-1.4).
  - Comportamento da barra lateral:
    - no desktop, recolhe para 90px; a escolha fica no `localStorage`;
    - abaixo de 992px, continua como gaveta (offcanvas-lg do Bootstrap).
  - Cabeçalho:
    - botão de menu;
    - busca de tarefas (no celular, vira um botão de ícone);
    - alternância de tema;
    - menu do usuário (dropdown do Bootstrap) com Minha conta, Meu consumo e Sair (POST).
- [ ] `feat(ui): toasts, modal de exclusão e paginação no novo visual`
  - `includes/messages.html`: toast com ícone por severidade.
  - `static/js/app.js`:
    - o Bootbox recebe `className`, ícone e botões no estilo do modal do DESIGN.md (T3-1.5 continua);
    - recolher a barra lateral e trocar o tema.
  - `includes/pagination.html`:
    - "Mostrando X–Y de N";
    - Anterior, números (`get_elided_page_range`) e Próxima;
    - todos os links continuam com `{% url_pagina %}` (T3-1.2).

### C. Telas
- [ ] `feat(ui): listas com filtros no cartão e tabelas que viram cartões no celular`
  - O padrão é o mesmo em todas as listas:
    - `page_head` com a ação "Novo";
    - um cartão com cabeçalho (título e contador) e os filtros (`includes/filtros.html`), que no celular ficam recolhidos num botão "Filtros";
    - `<table class="table table-cards">` com `data-label` em cada `td`;
    - a primeira coluna `lead`, as ações como botões de ícone, a paginação no rodapé e um estado vazio com o próximo passo.
  - Abaixo de 768px, o CSS transforma cada linha num cartão.
  - Listas: tarefas, projetos, estágios, equipes, anotações, apontamentos (com indicador do total de horas), quadros, usuários, requisições, IA por usuário e meu consumo.
- [ ] `feat(ui): telas de detalhe e formulários`
  - Os `*_detail.html` ganham:
    - trilha e `page_head` com Editar e Excluir;
    - um cartão de resumo em pares rótulo/valor (2 colunas);
    - cartões laterais para as seções relacionadas, como as anotações e os apontamentos da tarefa, ou os membros e estágios do projeto.
  - `crud/form.html`: cartão de até 720px, com rodapé Cancelar + Salvar, usando o `voltar` do `RetornoMixin`. `crud/confirm_delete.html` segue o mesmo visual do modal.
- [ ] `feat(projects): quadro kanban no novo visual`
  - Colunas em `--surface-2` com contador e "+".
  - Cartão de tarefa com:
    - faixa de prioridade;
    - etiqueta;
    - avatar com as iniciais do responsável;
    - prazo com ícone, em vermelho quando vencido;
    - botões ◀ ▶ de ícone (os mesmos POSTs de hoje).
  - Rolagem horizontal com *snap* no celular.
  - Nova propriedade `Task.vencida` (prazo anterior a hoje e estágio que não é concluído nem aprovado).
- [ ] `feat(pages): painel inicial com indicadores e progresso dos projetos`
  - Três indicadores com ícone e a lista de tarefas recentes com etiquetas.
  - Projetos recentes com barra de progresso. O progresso vem de `annotate` com `Count` filtrado (concluído e aprovado) no próprio queryset, sem queries extras (o `QueriesTests` continua valendo).
- [ ] `feat(accounts): entrar e criar conta em layout dividido, e Minha conta`
  - Novo `templates/auth_base.html`: formulário à esquerda, painel azul à direita, que some abaixo de 992px.
  - `registration/login.html` passa a estendê-lo. O cadastro ganha `accounts/cadastro.html` (só muda o `template_name` da view).
  - `accounts/conta.html`: cartão de perfil (avatar, nome, papel) e cartões Dados pessoais, Endereço e Perfil e redes, cada um com Editar.
- [ ] `feat(ia): assistente e telas de IA no novo visual`
  - Assistente: balões e área de envio no novo visual, coluna de apoio com a barra de cota e chips. Os ids e o `data-sugestao` ficam iguais, então o `assistente.js` não muda.
  - Configuração da IA: formulário à esquerda e cartão "Conexão" à direita, com "Testar conexão" no cabeçalho.
  - Requisição: resumo, pergunta e resposta em cartões.
- [ ] `feat(pages): página Sobre e páginas de erro no novo visual`
  - Sobre: texto e os dois diagramas em cartões `figure`. As imagens ganham fundo branco para continuarem legíveis no tema escuro.
  - Erros:
    - 403 e 404 dentro do layout, com número grande, frase e "Voltar ao início";
    - 400 e 500 com o mesmo visual, em `erro_simples.html`.

### D. Testes e documentação
- [ ] `test(ui): cobrir etiquetas, prazo vencido, progresso e estrutura das telas`
  - As templatetags de `ui` produzem a classe e o texto certos para cada prioridade, estágio, papel e situação.
  - `Task.vencida` vale nos dois sentidos.
  - O progresso no painel mostra a porcentagem certa, sem queries extras.
  - Toda lista renderiza `table-cards` com `data-label`.
  - O `base.html` traz a fonte, os ícones, o botão de tema e o link "Pular para o conteúdo".
  - A paginação numerada preserva os filtros.
  - Login e cadastro usam o layout dividido.
- [ ] `docs: registrar a nova interface no DESIGN.md e na matriz`
  - DESIGN.md: a seção 13 passa a descrever o que foi implementado.
  - `docs/criterios.md`: evidências de T3-2.5 atualizadas.

### E. Validação e entrega
- [ ] Rodar a suíte completa e o `coverage`.
- [ ] Verificar no navegador, no servidor local com o banco descartável e os dados do `popular_demo`:
  - os três papéis;
  - as larguras de 375, 768 e 1280px;
  - os temas claro e escuro;
  - a barra lateral recolhida e a gaveta;
  - os fluxos de mover, criar pelo "+", excluir com o Bootbox, filtrar e paginar, perguntar ao assistente e as máscaras;
  - o console sem erros e nenhuma página com rolagem horizontal.
- [ ] `/validate-criterion` em DEF-4, DEF-7, T1-1.5, T2-1.4, T2-2.3, T3-1.2, T3-1.4, T3-1.5, T3-2.3c e T3-2.5.
- [ ] Deploy no App Engine (`collectstatic`, `gerar_app_local.py`, `gcloud app deploy`) e conferência do site publicado logado.
- [ ] Enviar ao GitHub e mesclar na `main` somente quando o desenvolvedor pedir: primeiro `docs/design-tailadmin`, depois `feat/interface-tailadmin`.

## 3. Revisão de escopo por testes

- A suíte atual (124 testes) continua passando sem mudar regras. Isso inclui:
  - acesso por grupo;
  - posse de registros;
  - movimento das tarefas;
  - mensagens;
  - filtros com paginação;
  - assistente e IA;
  - queries sem N+1.
- Os testes novos estão na etapa D.
- Comando:

```bash
SECRET_KEY=teste DEBUG=False DATABASE_URL=postgres://naes@127.0.0.1:54329/naes GEMINI_API_KEY= .venv/bin/coverage run manage.py test && .venv/bin/coverage report
```

## 4. Adequação ao critério avaliativo

| Critério | Como fica |
|---|---|
| T3-2.5 (interface amigável e navegação coerente) | Reforçado pelo novo visual responsivo e consistente, verificado por papel e por largura. |
| DEF-4 e T1-1.5 (layout com framework front-end) | Continua o Bootstrap 5, agora com os tokens do TailAdmin. |
| DEF-7 e T3-1.5 (plugins jQuery) | O Bootbox e o jQuery Mask continuam funcionando; o Bootbox ganha o novo estilo. |
| T2-1.4 (`is_authenticated` nos menus) | Mantido na barra lateral e no cabeçalho. |
| T2-2.3 e T3-1.2 (paginação e templatetag própria) | A paginação numerada continua usando `url_pagina`, que preserva os filtros. |
| T3-1.4 (mensagens) | Os toasts mudam de visual, mas continuam usando o framework de mensagens. |
| T3-2.3c (assistente por AJAX, com CSRF, no visual do site) | Mantido, com os mesmos ids e o mesmo `assistente.js`. |

Ao final, rodar `/validate-criterion` nesses IDs.

## Arquivos principais

- `static/css/theme.css`, `static/js/app.js`.
- `templates/base.html`, `templates/auth_base.html` (novo) e `templates/includes/*`.
- `templates/projects/*`, `templates/pages/*`, `templates/accounts/*`, `templates/ia/*`, `templates/registration/login.html`, `templates/crud/*` e as páginas de erro.
- `pages/templatetags/ui.py` (novo).
- `projects/models.py` (`Task.vencida`).
- `pages/views.py` (progresso no painel).
- `accounts/views.py` (`template_name` do cadastro).
- Testes em `pages/tests.py` e `projects/tests.py`.
- Reaproveitados sem mudança:
  - `projects/templatetags/paginacao.py::url_pagina`;
  - o `RetornoMixin`, que fornece o `voltar` e o `next`;
  - o `static/js/assistente.js`;
  - o `includes/filtros.html` (só muda o visual);
  - o protótipo `docs/design/prototypes/interface-tailadmin.html`, como referência de marcação e CSS.
