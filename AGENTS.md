# AGENTS.md

Orientação para agentes de IA neste repositório. Este é o trabalho final da disciplina de Novas Aplicações em Engenharia de Software (NAES, IFPR 2026): um monolito **Django MVT** de gestão de equipes, projetos e tarefas em kanban.

## Prioridade

1. Cumprir os critérios de avaliação. A lista rastreável está em `docs/criterios.md`, e a fonte oficial é `../guidelines/NAES 2026 - Plano de Atividades e Avaliações.pdf`. Em caso de conflito, o PDF vence.
2. Entrega final em **04/12/2026** (recuperação do 3º trimestre). A apresentação regular é em 13/11/2026, por isso o núcleo vem antes da IA.
3. Em caso de dúvida sobre escopo, regra de negócio ou critério, **pergunte ao desenvolvedor** antes de decidir.

## Diretórios

Dentro do repositório:

- `config/`: settings, urls e wsgi.
- `accounts/`: usuário por e-mail, Profile, Address, cadastro, login, senha e grupos.
- `projects/`: Team, Project, Stage, Task, Note, TimeEntry, kanban e filtros.
- `pages/`: home e página "sobre".
- `ia/`: única porta de entrada para a IA (`ia/services.py::chamar_ia`) e assistente.
- `templates/`, `static/`: layout global e arquivos estáticos. `static_gcloud/` é gerado pelo `collectstatic`.
- `docs/criterios.md`: matriz critério, etapa, evidência e estado.
- `docs/escopo-legado.md`: escopo herdado do projeto antigo.
- `docs/plans/`: planejamentos com checkboxes.
- `docs/design/`: `DESIGN.md` (identidade visual) e `prototypes/`.
- `contexto_projeto.md`: contexto do sistema enviado ao assistente de IA.

Fora do repositório, somente leitura:

- `../guidelines/`: critérios, apostila de Django e guias de Google Cloud.
- `../outsourcing-deprecated/`: API DRF e Angular antigos. Consultar apenas para entender o escopo; não copiar a arquitetura.

## Comandos

```bash
source .venv/bin/activate
python manage.py check
python manage.py makemigrations --check
python manage.py test
coverage run manage.py test && coverage report
python manage.py runserver
python manage.py collectstatic --noinput
python manage.py popular_demo            # dados de demonstração (exige DEMO_SENHA); --remover apaga
python manage.py graph_models accounts projects --dot --disable-abstract-fields -X AbstractUser,AbstractBaseUser,PermissionsMixin,Group,Permission,BaseModel -o docs/design/classes.dot
dot -Tpng -Gdpi=110 docs/design/classes.dot -o static/img/diagrama-classes.png
python scripts/gerar_app_local.py && gcloud app deploy app.local.yaml
```

`.env` é obrigatório (`SECRET_KEY`, `DATABASE_URL`); veja `.env.example`.

## Convenções

- Código de domínio, comentários, mensagens e interface em português.
- Views baseadas em classe (`CreateView`, `UpdateView`, `DeleteView`, `DetailView`, `ListView`). Sem DRF, JWT ou SPA.
- Banco sempre PostgreSQL (Neon.tech). **Nunca** configurar SQLite, nem para testes.
- `accounts.User` precisa existir, com `AUTH_USER_MODEL` configurado, **antes** do primeiro `migrate`.
- Papéis são Groups do Django: Administrador, Gerente, Desenvolvedor. Cadastro público sempre entra como Desenvolvedor.
- Posse por usuário: `form_valid()` grava o dono e `get_queryset()` filtra. `Note` e `TimeEntry` (`author`) são estritamente privados, inclusive para administradores. `Project` (`created_by`) restringe o CRUD ao dono, mas aparece no quadro para os participantes.
- Toda view de cadastro, alteração e exclusão usa o framework de mensagens.
- Formulários com crispy-forms e Bootstrap 5.
- Chamadas à IA passam somente por `chamar_ia`.
- Segredos nunca entram no git (`.env`, chaves, `app.local.yaml`).

## Fluxo de trabalho

Skills em `.claude/skills/` (abra o Claude Code dentro deste diretório para carregá-las):

- `/plan-feature <input>`: planeja em `docs/plans/`.
- `/prototype-ui <input>`: protótipo clicável com três abordagens.
- `/validate-criterion <etapa ou critério>`: confere a implementação contra o critério.
- `/conventional-commits`: padroniza as mensagens de commit.

Ordem por feature: planejar, prototipar (se houver interface), implementar em commits pequenos, testar, validar o critério, marcar os checkboxes.
