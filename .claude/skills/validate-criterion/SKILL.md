---
name: validate-criterion
description: Valida se o que foi implementado em uma etapa satisfaz o critério de avaliação que pretende resolver, com evidências no código e em testes. Use ao concluir uma etapa, antes de marcar um critério como cumprido, ou quando pedirem para validar um critério.
argument-hint: "<ID do critério, etapa, plano ou 'todos'>"
---

# Validação de critério

Entrada: $ARGUMENTS

## Procedimento

1. Identifique os critérios-alvo em `docs/criterios.md`. Se a entrada for um plano ou etapa, use os IDs indicados nele.
2. Confronte o texto de cada critério com o PDF oficial (`../guidelines/NAES 2026 - Plano de Atividades e Avaliações.pdf`). O PDF vence em caso de divergência.
3. Busque a evidência real: leia models, views, urls, templates e settings. Não aceite a existência de um arquivo como prova; confirme que a funcionalidade está ligada de ponta a ponta (URL, view, template, menu).
4. Rode as verificações aplicáveis:
   - `python manage.py check` e `python manage.py makemigrations --check`;
   - os testes relacionados, ou `python manage.py test`;
   - para telas e permissões, exercite o fluxo no navegador ou com o test client, inclusive anônimo, grupo errado e usuário não dono.
5. Dê um veredito por item:

| ID | Veredito | Evidência | Pendência |
|---|---|---|---|
| T3-1.2 | Atende, Parcial ou Não atende | `arquivo:linha`, teste | o que falta |

6. Seja rigoroso: cada parte de um critério composto precisa de evidência própria. Na dúvida, o veredito é **Parcial**. Critério que dependa de ação externa não verificável aqui (deploy, TestAI) só é **Atende** com link ou comprovante informado pelo desenvolvedor.
7. Atualize `docs/criterios.md`: `[x]` e evidência somente para **Atende**. Se um item marcado deixou de atender, volte para `[ ]`.
8. Para Parcial ou Não atende, proponha a correção e pergunte ao desenvolvedor como seguir.
