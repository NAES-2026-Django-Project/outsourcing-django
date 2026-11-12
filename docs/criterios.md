# Critérios de avaliação

Fonte oficial: `../guidelines/NAES 2026 - Plano de Atividades e Avaliações.pdf`. Marque `[x]` somente depois de `/validate-criterion` confirmar a evidência. "Etapa" refere-se às etapas do plano geral (1 a 16).

## Definição do projeto

| | ID | Critério | Etapa | Evidência |
|---|---|---|---|---|
| [x] | DEF-1 | Pelo menos seis classes no models (sem contar User) | 5, 6 | `accounts/models.py`, `projects/models.py`, `ia/models.py` (12 classes além de User) |
| [x] | DEF-2 | Telas de inserir, alterar, excluir e listar para as classes, salvo regras de negócio | 7 | `projects/urls.py`, `projects/tests.py` |
| [x] | DEF-3 | Um movimento implementado, além do CRUD (mover tarefa entre estágios) | 8 | `TaskMoveView`, `MovimentoTests` |
| [x] | DEF-4 | Layout com Bootstrap, Tailwind, Bulma ou semelhante | 4 | `templates/base.html` |
| [x] | DEF-5 | Controle de acesso às páginas com autenticação | 5, 7 | `AcessoTests` |
| [x] | DEF-6 | Controle de acesso por grupos em mais de uma view | 7 | `accounts/mixins.py`, `AcessoTests` |
| [x] | DEF-7 | Plugins ou ferramentas com jQuery, Vue, React, Angular ou semelhante | 11 | jQuery, Bootbox e jQuery Mask em `templates/base.html` e `static/js/app.js` |
| [x] | DEF-8 | Controle de versões com Git | 1 | Repositório no GitHub, `main` com merges das ondas |

## 1º trimestre

| | ID | Critério | Etapa | Evidência |
|---|---|---|---|---|
| [x] | T1-1.1 | Criar um projeto Django | 1 | `config/` |
| [x] | T1-1.2 | URL, view e template da página "sobre" com descrição em texto | 4 | `pages/views.py`, `templates/pages/sobre.html` (inclui o assistente de IA) |
| [x] | T1-1.3 | Diagrama de caso de uso como imagem no template | 4 | `static/img/diagrama-casos-de-uso.png` |
| [x] | T1-1.4 | Diagrama de classes como imagem no template | 4 | `static/img/diagrama-classes.png`, gerado de `docs/design/classes.dot` com `accounts`, `projects` e `ia` (13 classes) |
| [x] | T1-1.5 | Template/layout com framework front-end | 4 | `templates/base.html` |
| [x] | T1-1.6 | Classes e atributos baseados no diagrama de classes | 5, 6 | `accounts/models.py`, `projects/models.py`, `ia/models.py`; o diagrama é gerado dos próprios models |
| [x] | T1-1.7 | Reutilizar e personalizar templates (`extra_context` ou `get_context_data`) | 4, 7 | `SobreView.extra_context`, `HomeView.get_context_data` |
| [x] | T1-2.1 | Views, urls e templates: CreateView | 7 | `projects/views.py` |
| [x] | T1-2.2 | Views, urls e templates: UpdateView | 7 | `projects/views.py` |
| [x] | T1-2.3 | Views, urls e templates: DeleteView | 7 | `projects/views.py` |
| [x] | T1-2.4 | Views, urls e templates: DetailView | 7 | `projects/views.py` |
| [x] | T1-2.5 | Views, urls e templates: ListView | 7 | `projects/views.py` |
| [x] | T1-2.6 | Instalar, ativar e aplicar Django Crispy Forms e complemento front-end | 7 | `templates/crud/form.html`, `crispy_bootstrap5` |
| [x] | T1-2.7 | PostgreSQL da Neon.tech, sem SQLite | 1, 5 | `DATABASES` via `DATABASE_URL` em `config/settings.py`; migrations aplicadas no Neon em 11/11/2026 |

## 2º trimestre

| | ID | Critério | Etapa | Evidência |
|---|---|---|---|---|
| [x] | T2-1.1 | Templates de todas as ListView, salvo regra de negócio | 7 | `templates/projects/*_list.html` |
| [x] | T2-1.2 | URLs de login, logout e alteração de senha | 5 | `accounts/urls.py`, `AutenticacaoTests` |
| [x] | T2-1.3 | `LoginRequiredMixin` nas views necessárias | 7 | `projects/views.py`, `AcessoTests` |
| [x] | T2-1.4 | `request.user.is_authenticated` para conteúdo dinâmico nos templates | 4 | `templates/includes/sidebar.html` |
| [x] | T2-1.5 | `form_valid()` guarda o User na chave estrangeira | 7 | `form_valid` em Project e Note, testes de posse |
| [x] | T2-1.6 | Editar somente os próprios registros | 7 | `PosseAnotacaoTests`, `PosseProjetoTests` |
| [x] | T2-1.7 | Excluir somente os próprios registros | 7 | `PosseAnotacaoTests`, `PosseProjetoTests` |
| [x] | T2-1.8 | Listar somente os próprios registros (`get_queryset()`) | 7 | `get_queryset`, testes de posse |
| [x] | T2-1.9 | Detalhar somente os próprios registros | 7 | `PosseAnotacaoTests`, `PosseProjetoTests` |
| [x] | T2-2.1 | QuerySets para retornar objetos a outras views (recentes etc.) | 4 | `HomeView` |
| [x] | T2-2.2 | Acesso às views por grupo (`GroupRequiredMixin`) | 7 | `accounts/mixins.py` |
| [x] | T2-2.3 | Paginação nas ListView (`paginate_by`) e links no template | 7 | `paginate_by`, `templates/includes/pagination.html` |
| [x] | T2-2.4 | Ativar e utilizar Django Debug Toolbar | 1, 10 | `config/settings.py`, `docs/otimizacao-queries.md` |
| [x] | T2-2.5 | Otimizar queries repetidas com `select_related` ou `prefetch_related` | 10 | `docs/otimizacao-queries.md`, `QueriesTests` |

## 3º trimestre

| | ID | Critério | Etapa | Evidência |
|---|---|---|---|---|
| [x] | T3-1.1 | Debug Toolbar, identificar queries repetidas e otimizá-las | 10 | `docs/otimizacao-queries.md`, `QueriesTests` |
| [x] | T3-1.2 | Django Filter em pelo menos duas ListView, com paginação por `templatetag` própria que preserve a busca | 9 | `projects/filters.py`, `projects/templatetags/paginacao.py`, `FiltrosTests` |
| [x] | T3-1.3 | Registros associados ao usuário em pelo menos duas classes (só ele lista, vê, altera e exclui) | 7 | `Note` e `TimeEntry`: `do_autor` em `projects/models.py`, `NoteAutorMixin` e `TimeEntryAutorMixin` em `projects/views.py`, fora do Django admin; `PosseAnotacaoTests`, `PosseApontamentoTests` |
| [x] | T3-1.4 | Framework de mensagens em cadastro, alteração e exclusão | 7, 11 | `SuccessMessageMixin` nas views, `MensagensECrudTests` |
| [x] | T3-1.5 | Pelo menos dois plugins jQuery distintos e funcionais | 11 | Bootbox e jQuery Mask em `static/js/app.js`, verificados no navegador |
| [x] | T3-1.6 | Deploy no Google App Engine e link de acesso | 12 | https://outsourcing-naes-2026.rj.r.appspot.com, publicado em 11/11/2026 e verificado logado (páginas do menu, Testar conexão e assistente); link no `README.md`; `app.yaml`, `scripts/gerar_app_local.py` |
| [x] | T3-2.1 | `AGENTS.md` e pelo menos três skills, uma para mensagens de commit | 2 | `AGENTS.md`, `.claude/skills/` |
| [x] | T3-2.2a | App `ia` como única porta de entrada para a IA | 13 | `ia/services.py::chamar_ia` é o único uso do SDK `google-genai` (Gemini) no código |
| [x] | T3-2.2b | Banco guarda configuração editável em tela, auditoria de cada chamada e cota mensal de tokens | 13 | `ConfiguracaoIA`, `ChamadaIA` e `CotaUsuario` em `ia/models.py`; `ChamarIATests` |
| [x] | T3-2.2c | Telas de requisições, configuração (com "Testar conexão"), IA por usuário e meu consumo | 14 | Telas em `ia/views.py` e `templates/ia/`; `TelasIATests` |
| [x] | T3-2.3a | Assistente usa `chamar_ia`, com contexto em `contexto_projeto.md` e instruções com limites | 15 | `perguntar_ao_assistente` usa `chamar_ia` com `contexto_projeto.md` e instruções com limites |
| [x] | T3-2.3b | Histórico por usuário, enviando à IA só as últimas mensagens (janela de 5) | 15 | `MensagemAssistente` por usuário e `janela_de_mensagens` (5); `AssistenteTests` |
| [x] | T3-2.3c | Perguntas por AJAX com CSRF, em tela no visual do site, com Markdown sanitizado | 15 | `static/js/assistente.js` (jQuery AJAX com `X-CSRFToken`), `ia/markdown.py` (nh3), `templates/ia/assistente.html`; verificado no navegador |
| [ ] | T3-2.4 | Auditoria do código na plataforma TestAI | 16 | |
| [x] | T3-2.5 | Sistema funcional, com interface amigável e fluxo de navegação coerente | 16 | Onda 4: retorno à origem (`RetornoMixin`), estágio pré-selecionado, excluir no detalhe, estados vazios, atalhos por papel e páginas 400/500; `NavegacaoTests`, `PaginasDeErroTests`; dados de `popular_demo` publicados; navegação verificada por papel (local) e logado em produção em 11/11/2026. Nova interface (12/11/2026): identidade do `docs/design/DESIGN.md`, responsiva (tabelas viram cartões, menu em gaveta), tema escuro; `InterfaceTests` |
