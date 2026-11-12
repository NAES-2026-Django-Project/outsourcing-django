# Onda 4: revisão final, navegação e dados de demonstração

- Status: em andamento
- Critérios: T3-2.5 (e revalidação de toda a matriz)
- Entrada: Onda 4: revisão final (T3-2.5): sistema funcional, interface amigável e fluxo de navegação coerente; passe completo de /validate-criterion na matriz; deploy final. TestAI (T3-2.4) fica para depois.

## Contexto

50 de 52 critérios estão `[x]`. Falta T3-2.5 ("entregar o sistema funcional, com interface amigável e fluxo de navegação coerente"); T3-2.4 (TestAI) fica para depois, a pedido do desenvolvedor. A revisão da navegação encontrou estes pontos:

- **Retorno quebra o fluxo:** criar anotação ou apontamento a partir da tarefa, ou criar e editar tarefa a partir do quadro, volta para a lista genérica. O botão "Cancelar" também vai para a lista. Todas as views usam `success_url` e `voltar` fixos (`projects/views.py`).
- **"Nova tarefa" no quadro** abre o formulário genérico, sem o estágio do projeto pré-selecionado.
- **Telas de detalhe sem "Excluir":** a exclusão só existe nas listas, com `data-excluir` e Bootbox.
- **Quadro vazio sem orientação:** colunas sem tarefas ficam em branco.
- **Home vazia sem próximo passo:** não há atalho por papel (criar projeto, abrir quadros).
- **Sem `500.html` e `400.html`:** com `DEBUG=False`, o App Engine mostra o texto cru do Django.
- **Banco sem dados de domínio:** o quadro aparece vazio na apresentação. O desenvolvedor escolheu um comando `popular_demo`.

Decisão do desenvolvedor: comando `manage.py popular_demo`, idempotente, com `--remover`, contas com e-mail `.test` e senha vinda do `.env`.

## 1. Revisão de configurações e ambiente

- [x] `pip check` sem problemas; `manage.py check` sem avisos
- [x] `makemigrations --check` sem mudanças; nenhuma migration pendente no Neon
- [x] Deploy funcionando (Onda 2) e IA verificada em produção (Onda 3)
- [x] Religar o PostgreSQL descartável de testes (porta 54329, hoje parado): `pg_ctl -D <scratchpad>/pg -o "-p 54329" start`
- [ ] Ação do desenvolvedor: definir `DEMO_SENHA` no `.env`. É a senha das contas de demonstração; não deve ser colada no chat.
- Nenhum pacote novo. `popular_demo` lê `DEMO_SENHA` de `os.environ`, já carregado por `environ.Env.read_env` em `config/settings.py`.

## 2. Etapas e commits

Branch: `feat/onda-4-revisao-final`.

### A. Navegação
- [x] `feat(projects): voltar à tela de origem após salvar ou cancelar`
  - Criar `RetornoMixin` em `projects/views.py`:
    - lê `?next=` e só aceita URL do próprio site, validada com `url_has_allowed_host_and_scheme`;
    - sobrescreve `get_success_url()`; quando há `next`, troca o `voltar` do contexto por ele.
  - Aplicar nas views de criar, editar e excluir de Task, Note e TimeEntry.
  - O formulário em `crud/form.html` não tem `action`, então o POST mantém a querystring e o `next` sem mudar o template.
  - Ajustar os links:
    - em `task_detail.html`, "Nova anotação", "Apontar horas" e "Editar" passam `next` com a URL da tarefa;
    - em `board.html`, "Nova tarefa" passa `next` com a URL do quadro.
- [x] `feat(projects): pré-selecionar o estágio ao criar tarefa pelo quadro`
  - `TaskCreateView.get_initial()` aceita `?estagio=`, somente entre os estágios de projetos em que o usuário participa (`Project.objects.com_participacao`).
  - O quadro ganha um botão "+" por coluna e um "Nova tarefa" que já abre no primeiro estágio.
- [x] `feat(projects): excluir a partir das telas de detalhe`
  - Botão "Excluir" com `data-excluir`, que reaproveita o Bootbox de `static/js/app.js`.
  - Telas: `team_detail`, `project_detail`, `stage_detail`, `task_detail`, `note_detail` e `timeentry_detail`.
  - O botão segue as permissões que a view de exclusão já aplica. Exemplo: equipe só para Administrador, usando `request.user.eh_administrador`.
- [x] `feat(projects): orientar o quadro sem tarefas`
  - Texto em colunas vazias.
  - Aviso com atalho para "Nova tarefa" quando o projeto não tem nenhuma tarefa.
- [x] `feat(pages): atalhos por papel na página inicial`
  - Gerente ou administrador sem projetos vê "Criar projeto".
  - Desenvolvedor sem projetos vê "peça ao gerente para incluir você".
  - Todos veem o link "Ver quadros".

### B. Páginas de erro
- [x] `feat(pages): páginas de erro 400 e 500`
  - Criar `templates/500.html` e `templates/400.html` independentes, sem `request` no contexto, que os handlers padrão do Django não fornecem.
  - Usar o CSS do tema e um link para o início.

### C. Dados de demonstração
- [x] `feat(projects): comando popular_demo com dados de demonstração`
  - Criar `projects/management/commands/popular_demo.py`.
  - Recusa rodar sem `DEMO_SENHA`.
  - Roda dentro de `transaction.atomic` e é idempotente (`get_or_create` por e-mail e nome).
  - Contas:
    - `gerente@outsourcing.test` (Gerente);
    - `dev1@outsourcing.test` e `dev2@outsourcing.test` (Desenvolvedor).
  - Dados:
    - a equipe "Equipe Demonstração", com o gerente e os devs;
    - os projetos "Portal do Cliente" e "App de Entregas", criados pelo gerente, que recebem os 4 estágios padrão pelo signal;
    - cerca de 12 tarefas com prioridades, prazos e responsáveis do projeto;
    - algumas anotações e apontamentos do `dev1`.
  - `--remover` apaga as contas `@outsourcing.test` e a equipe de demonstração, em cascata.
- [x] `docs: documentar DEMO_SENHA e o comando popular_demo`
  - `.env.example`, seção no `README.md` com as contas, sem a senha, e a linha de comando no `AGENTS.md`.

### D. Testes
- [x] `test(projects): cobrir retorno, pré-seleção e páginas de erro`
- [x] `test(projects): cobrir o comando popular_demo`

### E. Validação e entrega
- [x] Rodar a suíte inteira e o `coverage report`.
- [x] Navegação manual local no navegador como administrador, `gerente@outsourcing.test` e `dev1@outsourcing.test`:
  - mover tarefas;
  - criar a partir do quadro e da tarefa;
  - excluir pelo detalhe com Bootbox;
  - receber 403 com um papel sem permissão.
- [x] `/validate-criterion` em toda a matriz, registrando o veredito e a evidência.
- [ ] Rodar `popular_demo` no Neon. O banco é compartilhado com o site publicado.
- [ ] Deploy final: `collectstatic`, `scripts/gerar_app_local.py` e `gcloud app deploy app.local.yaml`. Depois, conferir o site publicado logado.
- [ ] `docs(criterios): marcar T3-2.5 como cumprido` e este plano como concluído.
- [x] `fix(projects): evitar nome repetido da equipe de demonstração` (achado na navegação manual)
- [x] Salvar este plano em `docs/plans/2026-11-11-onda-4-revisao-final.md` no primeiro commit da branch (`docs(plans): planejar a onda 4`).

## 3. Revisão de escopo por testes

- `next` interno é respeitado em salvar e cancelar; `next` externo (`https://evil.test`) é ignorado e cai no `success_url` padrão.
- `?estagio=` de um projeto em que o usuário não participa não é pré-selecionado.
- O botão "Excluir" do detalhe só aparece para quem pode excluir. A view de exclusão continua dando 403 ou 404 para os demais, como nos testes atuais.
- O quadro sem tarefas mostra a orientação, e a home mostra o atalho certo para cada papel.
- `500.html` e `400.html` renderizam sem `request`, e `handler500` responde 500 com o template do projeto.
- `popular_demo`:
  - cria as contas nos grupos certos e as tarefas válidas, com responsável membro do projeto;
  - rodar duas vezes não duplica nada;
  - `--remover` limpa tudo;
  - sem `DEMO_SENHA`, aborta com `CommandError`.
- A contagem de queries do quadro não cresce com o número de tarefas, como no `QueriesTests` atual.

Comando:

```bash
SECRET_KEY=teste DEBUG=False DATABASE_URL=postgres://naes@127.0.0.1:54329/naes GEMINI_API_KEY= .venv/bin/coverage run manage.py test && .venv/bin/coverage report
```

## 4. Adequação ao critério avaliativo

- **T3-2.5 (sistema funcional, interface amigável, navegação coerente):**
  - retorno à origem, pré-seleção, excluir no detalhe, estados vazios, atalhos da home e páginas de erro;
  - testes da etapa D;
  - dados de demonstração no site publicado;
  - navegação verificada por papel.
- **Revalidação de toda a matriz:** passe completo do `/validate-criterion`, para garantir que nada regrediu (DEF a T3-2.3).
- T3-2.4 (TestAI) continua `[ ]`, adiado pelo desenvolvedor.

Ao final, rodar `/validate-criterion T3-2.5` e depois o passe completo.

## Arquivos principais

- `projects/views.py`: `RetornoMixin` e `get_initial` da tarefa.
- `templates/projects/board.html`, `task_detail.html` e os demais `*_detail.html`.
- `templates/pages/home.html`, `templates/500.html` e `templates/400.html`.
- `projects/management/commands/popular_demo.py`.
- `projects/tests.py`.
- `.env.example`, `README.md`, `AGENTS.md` e `docs/criterios.md`.
- Reaproveitados:
  - `FormComUsuarioMixin` e `ExclusaoMixin` (`projects/views.py`);
  - `Project.objects.com_participacao` e `Task.objects.visiveis_para` (`projects/models.py`);
  - o Bootbox com `data-excluir` (`static/js/app.js`);
  - os estágios padrão criados pelo signal (`projects/signals.py`).
