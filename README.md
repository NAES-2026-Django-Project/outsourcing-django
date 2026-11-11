# Outsourcing

Sistema web de gestão de equipes, projetos e tarefas em quadro kanban, desenvolvido em Python e Django (arquitetura MVT) para a disciplina de Novas Aplicações em Engenharia de Software (IFPR, 2026).

## Como rodar

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha SECRET_KEY e DATABASE_URL (Neon.tech)
python manage.py migrate
python manage.py runserver
```

## Documentação

- [AGENTS.md](AGENTS.md): orientação para agentes de IA e convenções do projeto.
- [docs/criterios.md](docs/criterios.md): critérios de avaliação e estado de cada um.
- [docs/plans/](docs/plans/): planejamentos de implementação.
- [docs/design/DESIGN.md](docs/design/DESIGN.md): identidade visual.
