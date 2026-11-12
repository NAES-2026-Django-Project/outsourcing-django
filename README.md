# Outsourcing

Sistema web de gestão de equipes, projetos e tarefas em quadro kanban, desenvolvido em Python e Django (arquitetura MVT) para a disciplina de Novas Aplicações em Engenharia de Software (IFPR, 2026).

**Acesso:** https://outsourcing-naes-2026.rj.r.appspot.com

## Como rodar

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha SECRET_KEY e DATABASE_URL (Neon.tech)
python manage.py migrate
python manage.py runserver
```

## Dados de demonstração

Com `DEMO_SENHA` definida no `.env`:

```bash
python manage.py popular_demo            # cria ou completa os dados, sem duplicar
python manage.py popular_demo --remover  # apaga os dados de demonstração
```

O comando cria a equipe "Demonstração", os projetos "Portal do Cliente" e "App de Entregas" com doze tarefas, e três contas com a senha de `DEMO_SENHA`:

| Conta | Papel |
|---|---|
| `gerente@outsourcing.test` | Gerente, dono dos dois projetos |
| `dev1@outsourcing.test` | Desenvolvedor, com anotações e apontamentos |
| `dev2@outsourcing.test` | Desenvolvedor |

## Deploy no Google App Engine

Com o [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) instalado e o projeto selecionado (`gcloud init`):

```bash
python manage.py collectstatic --noinput
python scripts/gerar_app_local.py   # gera app.local.yaml com os segredos do .env, ignorado pelo git
gcloud app deploy app.local.yaml
gcloud app browse
```

Publicado no projeto `outsourcing-naes-2026`, região `southamerica-east1`. O banco é o mesmo Neon do ambiente local.

Na primeira publicação de um projeto novo, a conta de serviço do App Engine precisa de duas permissões (a primeira é a seção 6 do Guia 1; a segunda vem da mudança do Google, de 2024, que deixou de dar o papel de Editor às contas padrão):

```bash
gcloud storage buckets add-iam-policy-binding gs://staging.PROJETO.appspot.com --member=serviceAccount:PROJETO@appspot.gserviceaccount.com --role=roles/storage.admin
gcloud projects add-iam-policy-binding PROJETO --member=serviceAccount:PROJETO@appspot.gserviceaccount.com --role=roles/cloudbuild.builds.builder
```

O repositório `gae-standard` do Artifact Registry tem política de limpeza (seção 8 do Guia 1): mantém a tag `latest` e as duas versões mais recentes, e exclui o resto com mais de um dia.

## Documentação

- [AGENTS.md](AGENTS.md): orientação para agentes de IA e convenções do projeto.
- [docs/criterios.md](docs/criterios.md): critérios de avaliação e estado de cada um.
- [docs/plans/](docs/plans/): planejamentos de implementação.
- [docs/design/DESIGN.md](docs/design/DESIGN.md): identidade visual.
