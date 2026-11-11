---
name: conventional-commits
description: Padroniza mensagens de commit no formato Conventional Commits em português. Use sempre que for criar um commit neste repositório ou quando o desenvolvedor pedir para commitar.
argument-hint: "[escopo ou descrição opcional]"
---

# Conventional Commits

Contexto adicional do desenvolvedor: $ARGUMENTS

## Formato

```
tipo(escopo): descrição no imperativo, minúscula, sem ponto final

Corpo opcional explicando o porquê.
```

- **Tipos**: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `perf`, `build`, `chore`.
- **Escopos**: `accounts`, `projects`, `pages`, `ia`, `config`, `deploy`, `harness`, `design`. O escopo pode ser omitido em mudanças transversais.
- Assunto com até 72 caracteres, em português.
- Mudança incompatível: `tipo(escopo)!:` e rodapé `BREAKING CHANGE:`.

## Procedimento

1. Rode `git status` e `git diff` (inclusive `--staged`) e leia o que mudou.
2. Se a mudança misturar assuntos sem relação, **não faça um commit único**: divida em commits pequenos, adicionando arquivos pelo nome.
3. Confira que nada sensível será incluído (`.env`, chaves, `app.local.yaml`, `static_gcloud/`).
4. Escreva a mensagem no formato acima, descrevendo o que muda e por quê.
5. Se o commit concluir um item de `docs/plans/`, marque o checkbox correspondente no mesmo commit.
6. Não faça push sem pedido do desenvolvedor.

## Exemplos

```
feat(projects): adicionar movimentação de tarefas entre estágios
fix(accounts): impedir escolha de grupo no cadastro público
docs(harness): registrar skill de validação de critérios
```
