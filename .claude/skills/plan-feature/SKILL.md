---
name: plan-feature
description: Planeja a adequação ou implementação de uma feature do projeto, em etapas com commits pequenos, testes e vínculo com os critérios de avaliação. Use quando o desenvolvedor pedir para planejar uma feature, etapa ou adequação.
argument-hint: "<feature, etapa ou adequação a planejar>"
---

# Planejamento de feature

Entrada: $ARGUMENTS

Use o **plan mode** do Claude Code para montar o plano. Leia `AGENTS.md`, `docs/criterios.md` e, se útil, `docs/escopo-legado.md`. Pergunte ao desenvolvedor (`AskUserQuestion`) quando houver dúvida de escopo ou regra de negócio; não presuma.

Independente da entrada, o plano **sempre** tem estas quatro seções:

## 1. Revisão de configurações e ambiente

Todas as dependências para implementar já estão resolvidas? Verifique de fato, sem supor:

- pacotes em `requirements.txt` e instalados na `.venv`;
- `INSTALLED_APPS`, middleware e demais settings;
- variáveis em `.env` e `.env.example`;
- migrations pendentes (`makemigrations --check`) e acesso ao banco;
- features anteriores das quais esta depende;
- ações manuais do desenvolvedor (contas, chaves, credenciais).

## 2. Etapas e commits

Divida em etapas. Cada etapa lista os commits planejados, pequenos, já no formato Conventional Commits (skill `conventional-commits`), com checkboxes.

## 3. Revisão de escopo por testes

Liste os testes que provam que o sistema funciona como esperado: caminho feliz, permissões (anônimo, grupo errado, usuário não dono) e regras de negócio. Inclua o comando para rodá-los.

## 4. Adequação ao critério avaliativo

Cite os IDs de `docs/criterios.md` que a feature resolve e qual evidência (arquivo, tela, teste) comprovará cada um. Encerre indicando rodar `/validate-criterion`.

## Saída

Salve o plano aprovado em `docs/plans/AAAA-MM-DD-slug.md`, com este cabeçalho:

```markdown
# <Título>

- Status: em andamento
- Critérios: <IDs>
- Entrada: <texto informado>
```

Todo item acionável usa `- [ ]`. Durante a implementação, marque `- [x]` assim que o item for concluído e mude o status para `concluído` ao final.
