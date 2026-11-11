---
name: prototype-ui
description: Cria protótipo funcional clicável de uma interface como Claude artifact, com pelo menos três abordagens e identidade visual consistente. Use quando o desenvolvedor pedir para prototipar uma tela, fluxo ou interface.
argument-hint: "<tela, fluxo ou interface a prototipar>"
---

# Prototipação de interface

Entrada: $ARGUMENTS

Atue como um profissional de engenharia de software especializado em interface e experiência de usuário.

## Procedimento

1. Leia `docs/design/DESIGN.md`. Ele é a referência obrigatória de cores, fontes e decisões. Se não existir, crie-o antes de prototipar.
2. Leia `docs/escopo-legado.md` e os models envolvidos para usar dados e regras realistas, com textos em português.
3. Defina **pelo menos três abordagens** realmente diferentes para o escopo pedido (por exemplo: quadro kanban, lista com painel de detalhe, tabela densa), cada uma baseada em experiência de usuário e padrões de mercado.
4. Construa **um protótipo funcional clicável** publicado como Claude artifact, com um seletor para alternar entre as abordagens. Navegação, formulários, estados vazios, erros e mensagens devem responder a cliques. Antes de publicar, siga as orientações de artefatos disponíveis na sessão.
5. Use Bootstrap 5 e os tokens de `DESIGN.md`, para que o protótipo seja transferível para templates Django.
6. Salve o HTML em `docs/design/prototypes/<slug>.html`.
7. Apresente o link e, para cada abordagem, prós, contras e quando é indicada, com uma recomendação.
8. Pergunte ao desenvolvedor qual abordagem seguir. Não implemente os templates antes da escolha.
9. Registre a decisão em `DESIGN.md`, na tabela de decisões. Atualize tokens somente se surgir uma decisão nova, mantendo a mesma identidade em todos os protótipos.
