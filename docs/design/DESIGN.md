# Identidade visual

Referência obrigatória para protótipos e templates. Atualize somente quando houver uma decisão nova.

## Direção

Ferramenta de trabalho, com leitura rápida e densidade moderada. Azul-petróleo como cor de ação, neutros levemente esverdeados e prioridade comunicada por faixa lateral e etiqueta.

## Cores

| Token | Claro | Escuro | Uso | Bootstrap |
|---|---|---|---|---|
| `--paper` | `#f3f6f5` | `#11191c` | fundo da página | `--bs-body-bg` |
| `--surface` | `#ffffff` | `#1a2529` | cartões, barras | `--bs-tertiary-bg` |
| `--ink` | `#16262e` | `#e6edeb` | texto | `--bs-body-color` |
| `--muted` | `#5b6b70` | `#9aaaae` | texto secundário | `--bs-secondary-color` |
| `--line` | `#d7dfdd` | `#2e3c40` | bordas | `--bs-border-color` |
| `--accent` | `#0b6e69` | `#4fbdb4` | ações, item ativo | `--bs-primary` |
| `--on-accent` | `#ffffff` | `#06211f` | texto sobre accent | |
| `--accent-soft` | `#dcefed` | `#1d3a3a` | hover, colunas do kanban | `--bs-primary-bg-subtle` |
| `--highlight` | `#c8791a` | `#e5a14a` | destaques pontuais | |
| `--ok` | `#2e7d4f` | `#6cc08d` | sucesso | `--bs-success` |
| `--warn` | `#a86f12` | `#e0ad55` | atenção, prioridade alta | `--bs-warning` |
| `--danger` | `#b3392f` | `#ec8177` | erro, exclusão, urgente | `--bs-danger` |

## Tipografia

- Títulos: **Manrope** (600 a 800).
- Texto e interface: **IBM Plex Sans** (400 a 600).
- Números em tabelas: `font-variant-numeric: tabular-nums`.
- Escala: título de página 24px, seção 16px, texto 15px, apoio 13px, rótulos 12px.

## Componentes

- Raio: 6px em controles, 8px em cartões.
- Prioridade: faixa esquerda no cartão e etiqueta. Baixa `--muted`, Média `--accent`, Alta `--warn`, Urgente `--danger`.
- Mensagens do Django: toast no canto inferior direito, com faixa pela severidade.
- Exclusão: sempre confirmada em diálogo (Bootbox na implementação).
- Interface em português, com botões que dizem a ação ("Novo projeto", "Excluir").

## Implementação

Bootstrap 5 com as variáveis `--bs-*` sobrescritas em `static/css/theme.css` conforme a tabela. Os protótipos usam CSS próprio com os mesmos tokens, porque a política de segurança dos artifacts bloqueia folhas de estilo de CDN.

## Decisões

| Data | Tela | Decisão | Motivo |
|---|---|---|---|
| 11/11/2026 | Layout base | Abordagem A: barra lateral fixa com grupos de menu e barra superior com busca e usuário | Comporta todos os menus, inclusive os de IA, e segue o padrão de painéis em Bootstrap. Protótipo em `prototypes/layout-base.html` |
| 11/11/2026 | Assistente de IA | Pendente de escolha do desenvolvedor | Protótipo em `prototypes/assistente.html` com página de conversa, painel lateral e conversa com apoio |
