# Identidade visual

Referência obrigatória para protótipos e templates do Outsourcing. Toda tela nova segue este documento; toda decisão nova entra na tabela de [Decisões](#14-decisões).

Protótipo de referência com todas as telas: `prototypes/interface-tailadmin.html`, publicado em https://claude.ai/artifact/Qo296wGA8fiFjxLpa6wzMJ.

## 1. Princípios

| Princípio | O que significa no Outsourcing |
|---|---|
| **Clareza** | Cada tela tem um título, uma ação principal e um conteúdo principal. Ex.: "Tarefas" com o botão "Nova tarefa" e a tabela filtrável. |
| **Consistência** | O mesmo problema tem sempre a mesma solução: listas usam o mesmo cabeçalho, filtros, tabela e paginação; detalhes usam o mesmo cartão de resumo; formulários usam o mesmo cartão estreito com Salvar e Cancelar. |
| **Densidade confortável** | É uma ferramenta de trabalho: tabelas com linhas de 52px, cartões com respiro de 20 a 24px, sem decoração que não informe nada. |
| **Ação evidente** | Um único botão primário (azul) por área. Ações secundárias em botão contornado; destrutivas em vermelho e sempre confirmadas. |
| **Estado visível** | Prioridade, papel, situação da IA e cota aparecem como etiqueta, faixa ou barra, e não só como texto. |
| **Acessível** | Contraste AA em todos os textos, foco sempre visível, alvos de toque de 44px, ícones com rótulo. |
| **Responsivo** | Funciona de 375px a telas largas: menu vira gaveta, tabelas viram cartões, o quadro rola na horizontal. |

## 2. Inspiração: TailAdmin

A interface segue o **TailAdmin**, painel administrativo que o frontend antigo usava (`outsourcing-deprecated/outsourcing-frontend/src/styles.css`). Adotamos dele:

- a paleta (brand `#465FFF`, cinzas frios, sucesso, aviso, erro e informação) e a fonte **Outfit**;
- a estrutura: barra lateral branca com grupos em maiúsculas, cabeçalho fixo com borda inferior, conteúdo sobre fundo cinza muito claro;
- os componentes: cartões com raio de 16px e borda fina, tabelas com cabeçalho cinza pequeno, etiquetas em pílula com fundo suave, botões com raio de 8px e sombra discreta, campos de 44px com anel de foco azul translúcido;
- as sombras `theme-xs`, `theme-sm` e `theme-md`.

O que muda em relação ao TailAdmin original: ele é feito em Tailwind e Angular; aqui os mesmos tokens **sobrescrevem as variáveis do Bootstrap 5** (critério DEF-4/T1-1.5 continua atendido pelo Bootstrap), e os ícones são do **Bootstrap Icons**.

## 3. Cores

### 3.1 Escalas (iguais às do TailAdmin)

| Escala | 50 | 100 | 200 | 400 | 500 | 600 | 700 |
|---|---|---|---|---|---|---|---|
| brand | `#ecf3ff` | `#dde9ff` | `#c2d6ff` | `#7592ff` | `#465fff` | `#3641f5` | `#2a31d8` |
| gray | `#f9fafb` | `#f2f4f7` | `#e4e7ec` | `#98a2b3` | `#667085` | `#475467` | `#344054` |
| success | `#ecfdf3` | `#d1fadf` | `#a6f4c5` | `#32d583` | `#12b76a` | `#039855` | `#027a48` |
| warning | `#fffaeb` | `#fef0c7` | `#fedf89` | `#fdb022` | `#f79009` | `#dc6803` | `#b54708` |
| error | `#fef3f2` | `#fee4e2` | `#fecdca` | `#f97066` | `#f04438` | `#d92d20` | `#b42318` |
| info (blue-light) | `#f0f9ff` | `#e0f2fe` | `#b9e6fe` | `#36bffa` | `#0ba5ec` | `#0086c9` | `#026aa2` |

Cinzas escuros: gray-800 `#1d2939`, gray-900 `#101828`, gray-dark `#1a2231`.

### 3.2 Tokens semânticos

Telas e templates usam **somente** estes tokens, nunca a escala direto.

| Token | Claro | Escuro | Uso | Bootstrap |
|---|---|---|---|---|
| `--bg` | gray-50 `#f9fafb` | gray-900 `#101828` | fundo da página | `--bs-body-bg` |
| `--surface` | `#ffffff` | gray-dark `#1a2231` | barra lateral, cabeçalho, cartões | `--bs-tertiary-bg` |
| `--surface-2` | gray-50 `#f9fafb` | `#202a3b` | cabeçalho de tabela, coluna do quadro, hover | `--bs-secondary-bg` |
| `--text` | gray-800 `#1d2939` | `#e4e7ec` | títulos e texto principal | `--bs-body-color` |
| `--text-2` | gray-700 `#344054` | `#c4cad4` | texto de apoio em corpo | |
| `--muted` | gray-500 `#667085` | gray-400 `#98a2b3` | rótulos, legendas, cabeçalhos de tabela | `--bs-secondary-color` |
| `--border` | gray-200 `#e4e7ec` | gray-800 `#1d2939` | bordas de cartões e campos | `--bs-border-color` |
| `--border-soft` | gray-100 `#f2f4f7` | `#243042` | divisórias internas, linhas de tabela | |
| `--brand` | brand-500 `#465fff` | brand-500 `#465fff` | botão primário, links, foco | `--bs-primary` |
| `--brand-hover` | brand-600 `#3641f5` | brand-400 `#7592ff` | hover do primário | |
| `--brand-soft` | brand-50 `#ecf3ff` | `rgba(70,95,255,.14)` | item de menu ativo, etiqueta azul | `--bs-primary-bg-subtle` |
| `--brand-text` | brand-500 `#465fff` | brand-400 `#7592ff` | texto azul sobre fundo claro/escuro | `--bs-primary-text-emphasis` |
| `--success` / `--success-soft` / `--success-text` | 500 / 50 / 700 | 500 / `rgba(18,183,106,.15)` / 400 | sucesso, concluído | `--bs-success` |
| `--warning` / `--warning-soft` / `--warning-text` | 500 / 50 / 700 | 500 / `rgba(247,144,9,.15)` / 400 | atenção, prioridade alta | `--bs-warning` |
| `--error` / `--error-soft` / `--error-text` | 500 / 50 / 700 | 500 / `rgba(240,68,56,.15)` / 400 | erro, exclusão, urgente | `--bs-danger` |
| `--info` / `--info-soft` / `--info-text` | 500 / 50 / 700 | 500 / `rgba(11,165,236,.15)` / 400 | informação, gerente | `--bs-info` |

Regras de contraste (AA):

- texto de etiqueta no tema claro usa o tom **700** sobre o **50** (o 600 do TailAdmin fica abaixo de 4,5:1);
- no tema escuro, etiquetas usam o tom **400** sobre o fundo translúcido do 500;
- `--brand` sobre branco e texto branco sobre `--brand` têm 4,8:1;
- `--muted` só para texto de apoio, nunca para a informação principal da linha.

### 3.3 Mapeamentos de estado

| Conceito | Valor | Etiqueta |
|---|---|---|
| Prioridade | Baixa | gray (`--surface-2` + `--text-2`) |
| | Média | info |
| | Alta | warning |
| | Urgente | error |
| Estágio | Backlog | gray |
| | Em andamento | brand |
| | Concluído | success |
| | Aprovado | success com ícone de verificado |
| Papel | Administrador | brand |
| | Gerente | info |
| | Desenvolvedor | gray |
| Situação da chamada à IA | Sucesso | success |
| | Erro | error |
| | Recusada pelo modelo | warning |
| | Bloqueada pela cota | gray |
| Cota | até 70% | barra brand |
| | 70% a 90% | barra warning |
| | acima de 90% | barra error |

## 4. Tipografia

- Fonte única: **Outfit** (Google Fonts, pesos 400, 500, 600 e 700), com fallback `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`.
- Números em tabelas, indicadores e horas: `font-variant-numeric: tabular-nums`.
- Títulos com `text-wrap: balance`.

| Papel | Tamanho / altura de linha | Peso | Exemplo |
|---|---|---|---|
| Título da página | 24 / 32 | 600 | "Tarefas" |
| Número de indicador | 30 / 38 | 600 | "20" tarefas abertas |
| Título de cartão | 18 / 28 | 600 | "Tarefas recentes" |
| Subtítulo de seção | 16 / 24 | 600 | "Minhas anotações" |
| Texto | 14 / 20 | 400 | linhas de tabela, formulários |
| Apoio e rótulos | 12 / 18 | 500 | cabeçalho de tabela, legendas, etiquetas |
| Grupo do menu | 12 / 18, maiúsculas, espaçamento 0,04em | 500 | "TRABALHO" |

## 5. Espaçamento, raio e sombra

- **Grade de 4px.** Valores usados: 4, 8, 12, 16, 20, 24, 32, 40.
- Espaço entre cartões e seções da página: 24px no desktop, 16px no celular.
- Padding de cartão: 20px 24px no cabeçalho e 24px no corpo (16px no celular).
- **Raio:** 8px em botões, campos, menus e itens de menu; 12px em cartões do quadro e balões do chat; 16px em cartões; 999px em etiquetas e avatares.
- **Sombra:**
  - `xs` `0 1px 2px rgba(16,24,40,.05)`: botões e campos;
  - `sm` `0 1px 3px rgba(16,24,40,.1), 0 1px 2px rgba(16,24,40,.06)`: cartão do quadro em hover;
  - `md` `0 4px 8px -2px rgba(16,24,40,.1), 0 2px 4px -2px rgba(16,24,40,.06)`: menus suspensos, toasts e modal.
- Cartões de página não têm sombra, só borda (como no TailAdmin).

## 6. Layout

```
┌──────────────┬───────────────────────────────────────────────┐
│ Logo         │ ☰  Buscar tarefas…         ☾  🔔  Avatar ▾    │  cabeçalho 64px, fixo
│──────────────│───────────────────────────────────────────────│
│ TRABALHO     │ Início / Tarefas                              │  trilha
│ ▣ Início     │ Tarefas                        [+ Nova tarefa]│  cabeçalho da página
│ ▣ Quadros    │ ┌───────────────────────────────────────────┐ │
│ ▣ Tarefas    │ │ filtros                                   │ │
│ GESTÃO       │ ├───────────────────────────────────────────┤ │
│ ▣ Projetos   │ │ tabela / cartões                          │ │
│ IA           │ └───────────────────────────────────────────┘ │
│ SISTEMA      │                                               │
└──────────────┴───────────────────────────────────────────────┘
  290px (recolhida: 90px, só ícones)    conteúdo: padding 24px, máx. 1440px
```

- **Barra lateral:** fundo `--surface`, borda direita `--border`, logo no topo (altura 64px), grupos Trabalho, Gestão, Inteligência artificial e Sistema. Item: ícone 20px + texto 14/20 peso 500, padding 8px 12px, raio 8px. Ativo: fundo `--brand-soft`, texto e ícone `--brand-text`. Hover: `--surface-2`. Grupos sem permissão não aparecem.
- **Tema:** claro por padrão; o escuro só vale quando a pessoa escolhe no botão do cabeçalho.
- **Cabeçalho:** fundo `--surface`, borda inferior, fixo. Botão de menu (recolhe no desktop, abre a gaveta no celular), busca de tarefas, alternância de tema, avatar com nome e menu (Minha conta, Sair).
- **Conteúdo:** trilha de navegação (12/18 `--muted`), linha de título com ação principal à direita, e as seções empilhadas com 24px de espaço.
- **Páginas públicas** (entrar, criar conta): tela dividida; à esquerda o formulário em cartão de até 440px, à direita um painel `--brand` com a proposta do sistema (oculto abaixo de 992px).

## 7. Responsividade

Pontos de quebra do Bootstrap: `sm` 576, `md` 768, `lg` 992, `xl` 1200, `xxl` 1400.

| Componente | ≥ 992px | 768–991px | < 768px |
|---|---|---|---|
| Barra lateral | fixa, recolhível para 90px | gaveta sobre o conteúdo, com fundo escurecido | gaveta |
| Cabeçalho | busca visível | busca visível | busca vira botão de ícone; nome do usuário oculto |
| Cabeçalho da página | título e ação na mesma linha | igual | ação abaixo do título, largura total |
| Indicadores | 3 ou 4 por linha | 2 por linha | 1 por linha |
| Tabelas | tabela | tabela com rolagem horizontal no próprio cartão | lista de cartões: título da linha em destaque, demais campos como pares rótulo/valor, ações no rodapé |
| Filtros | uma linha | duas colunas | recolhidos atrás do botão "Filtros" |
| Quadro | 4 colunas lado a lado | rolagem horizontal, colunas de 280px | rolagem horizontal com *snap*, coluna de 85% da tela |
| Formulários | cartão de até 720px, campos em duas colunas quando curtos | duas colunas | uma coluna; botões em largura total |
| Assistente | conversa + coluna de apoio de 320px | coluna de apoio abaixo | coluna de apoio abaixo, recolhível |

Regra geral: a página nunca rola na horizontal; só o quadro e tabelas largas rolam, dentro do próprio contêiner.

## 8. Componentes

### Botões

| Variante | Aparência | Uso |
|---|---|---|
| Primário | fundo `--brand`, texto branco, sombra xs; hover `--brand-hover` | uma ação principal por área: "Nova tarefa", "Salvar", "Entrar" |
| Secundário | fundo `--surface`, borda `--border`, texto `--text-2`; hover `--surface-2` | Editar, Cancelar, Voltar, Filtrar |
| Perigo | fundo `--error`, texto branco (no modal) ou contorno `--error-text` (na tela) | Excluir |
| Só ícone | 36×36px (44px no celular), raio 8px, sempre com `aria-label` e `title` | mover tarefa, menu, tema |

Tamanhos: padrão 44px de altura (padding 10px 16px, texto 14/20 peso 500); compacto 36px (`btn-sm`) em tabelas e cartões. Ícone à esquerda do texto, 16px, gap 8px.

### Campos

- Altura 44px, raio 8px, borda `--border`, fundo `--surface`, sombra xs, padding 10px 14px, texto 14px.
- Rótulo acima (14/20 peso 500 `--text-2`); ajuda abaixo (12/18 `--muted`).
- Foco: borda `--brand-200`/`--brand` e anel `0 0 0 4px rgba(70,95,255,.12)`.
- Erro: borda `--error`, anel vermelho translúcido e mensagem 12/18 `--error-text` com ícone.
- Seleção com seta própria; área de texto com altura mínima de 120px; caixa de seleção 20px com marca `--brand`.
- Desabilitado: fundo `--surface-2`, texto `--muted`.

### Etiquetas

Pílula com padding 2px 10px, texto 12/18 peso 500, fundo `*-soft` e texto `*-text` (ver 3.3). Opcionalmente um ponto de 6px à esquerda.

### Cartão

Fundo `--surface`, borda `--border`, raio 16px. Cabeçalho opcional (título 18/28 + descrição 14/20 `--muted` + ações à direita) separado do corpo por `--border-soft`.

### Indicador (cartão de número)

Ícone 24px dentro de um quadrado de 48px com raio 12px e fundo `--surface-2`; rótulo 14/20 `--muted`; número 30/38 peso 600; variação opcional em etiqueta.

### Cabeçalho da página

Trilha (Início / Seção / Item) + título 24/32 + descrição opcional + ações (primária por último, à direita).

### Tabela

Dentro de um cartão sem padding no corpo. Cabeçalho com fundo `--surface-2`, texto 12/18 peso 500 `--muted`; linhas de 52px com divisória `--border-soft`, hover `--surface-2`. A primeira coluna leva o link para o detalhe. Coluna de ações à direita com botões compactos (Editar, Excluir). Números alinhados à direita e tabulares.

### Filtros

Faixa no topo do cartão da lista: campos compactos (40px) lado a lado, botão "Filtrar" e link "Limpar". Mostra a quantidade de resultados ("12 tarefas").

### Paginação

Rodapé do cartão: "Mostrando 1–10 de 32" à esquerda; à direita, Anterior, números (ativo com fundo `--brand-soft`) e Próxima. Os links preservam os filtros (templatetag `url_pagina`).

### Estado vazio

Ícone 32px em círculo `--surface-2`, título 16/24, uma frase com o próximo passo e o botão da ação ("Criar projeto").

### Toast

Canto inferior direito, cartão `--surface` com sombra md, raio 12px, ícone colorido pela severidade (sucesso, aviso, erro, informação), texto 14/20 e botão de fechar. Some em 4 segundos.

### Modal de confirmação

Fundo escurecido `rgba(16,24,40,.5)` com desfoque leve; cartão de até 440px, ícone de alerta em círculo `--error-soft`, título "Excluir tarefa?", frase com o nome do registro e "Esta ação não pode ser desfeita.", botões Cancelar (secundário) e Excluir (perigo). Esc e clique fora cancelam. Na implementação, o Bootbox recebe essas classes.

### Cartão do quadro (kanban)

Fundo `--surface`, borda `--border`, raio 12px, faixa esquerda de 3px na cor da prioridade, padding 12px. Título 14/20 peso 500 (link); linha de metadados: etiqueta de prioridade, avatar com iniciais do responsável, prazo com ícone (vermelho se vencido). Botões ◀ ▶ só ícone no rodapé. O cartão também pode ser arrastado e solto em outra coluna (SortableJS 1.15.2; no toque, segurar 200ms antes de arrastar); durante o arraste as colunas ganham contorno tracejado e o cartão de origem fica translúcido. As setas continuam como alternativa acessível por teclado. Coluna: fundo `--surface-2`, raio 16px, cabeçalho com nome, contador em pílula e botão "+".

### Chat do assistente

Balões com raio 12px e largura máxima de 80%: do usuário à direita em `--brand` com texto branco; do assistente à esquerda em `--surface-2` com Markdown (listas, negrito, código). Indicador "digitando…" com três pontos. Campo de envio fixo no rodapé do cartão.

### Barra de cota

Altura 8px, raio 999px, trilho `--surface-2`, preenchimento conforme 3.3, legenda "1.562 de 200.000 tokens (1%)".

## 9. Padrões de tela

| Padrão | Estrutura | Telas |
|---|---|---|
| Painel | cabeçalho, linha de indicadores, cartões lado a lado | Início, Meu consumo |
| Lista | cabeçalho com ação "Novo", cartão com filtros, tabela e paginação | Tarefas, Projetos, Estágios, Equipes, Anotações, Apontamentos, Usuários, Requisições, IA por usuário, Quadros |
| Detalhe | cabeçalho com Editar e Excluir, cartão de resumo em pares rótulo/valor (2 colunas), cartões de seções relacionadas | Tarefa, Projeto, Estágio, Equipe, Anotação, Apontamento, Requisição |
| Formulário | trilha, título, cartão de até 720px com campos e rodapé "Cancelar" + "Salvar" | todos os cadastros e edições, conta, cota, configuração da IA |
| Quadro | cabeçalho com equipe, membros e "Nova tarefa"; colunas de estágios | Quadro do projeto |
| Conversa | chat à esquerda, coluna de apoio à direita | Assistente |
| Autenticação | tela dividida, sem barra lateral | Entrar, Criar conta |
| Erro | centralizado, número grande, frase e "Voltar ao início" | 400, 403, 404, 500 |

## 10. Ícones

Bootstrap Icons 1.11.3 (`<i class="bi bi-…" aria-hidden="true">` no Django; SVG embutido no protótipo).

| Uso | Ícone | Uso | Ícone |
|---|---|---|---|
| Início | `house` | Novo / adicionar | `plus-lg` |
| Quadros | `kanban` | Editar | `pencil` |
| Tarefas | `list-check` | Excluir | `trash3` |
| Minhas anotações | `journal-text` | Voltar | `arrow-left` |
| Meus apontamentos | `clock-history` | Filtrar | `funnel` |
| Meus projetos | `folder2-open` | Limpar / fechar | `x-lg` |
| Estágios | `layout-three-columns` | Buscar | `search` |
| Equipes | `people` | Mover tarefa | `chevron-left`, `chevron-right` |
| Usuários | `person-gear` | Enviar pergunta | `send` |
| Assistente | `chat-dots` | Testar conexão | `plug` |
| Meu consumo | `speedometer2` | Tema claro / escuro | `sun`, `moon-stars` |
| Configuração da IA | `sliders` | Menu / recolher | `list`, `layout-sidebar-inset` |
| Requisições | `activity` | Prazo | `calendar3` |
| IA por usuário | `bar-chart` | Sucesso / aviso / erro | `check-circle`, `exclamation-triangle`, `x-circle` |
| Minha conta | `person-circle` | Estado vazio | `inbox` |
| Sobre | `info-circle` | Senha | `shield-lock` |
| Sair / Entrar | `box-arrow-right`, `box-arrow-in-right` | Criar conta | `person-plus` |

Ícones decorativos levam `aria-hidden="true"`; botões só com ícone levam `aria-label`.

## 11. Textos da interface

- Português, frases curtas, voz ativa. Botões dizem a ação: "Nova tarefa", "Salvar alterações", "Excluir projeto", "Testar conexão".
- Mensagens após ações: "Tarefa cadastrada.", "Tarefa movida para Em andamento.", "Projeto excluído." (framework de mensagens, como toast).
- Erros dizem o que fazer: "O responsável precisa participar do projeto.", "Mova ou exclua as tarefas antes de excluir este estágio."
- Estados vazios indicam o próximo passo: "Você ainda não tem projetos. Crie um para a sua equipe."
- Datas `dd/mm/aaaa`, horas `14h30`, números com separador de milhar (`200.000`).

## 12. Acessibilidade

- Contraste AA (4,5:1 para texto, 3:1 para ícones e bordas de controles) nos dois temas, conforme 3.2.
- Foco visível em todo elemento interativo: anel de 4px `rgba(70,95,255,.25)` + borda `--brand`.
- Alvos de toque de no mínimo 44×44px no celular (botões de ícone crescem de 36 para 44px).
- Navegação completa por teclado: gaveta e modal prendem o foco e fecham com Esc; o primeiro link da página é "Pular para o conteúdo".
- Estado nunca só por cor: etiquetas têm texto; prazo vencido tem ícone e texto.
- `prefers-reduced-motion`: sem animações de deslize, só troca de opacidade.

## 13. Implementação no Django

Implementado em 12/11/2026 (plano `docs/plans/2026-11-12-aplicar-interface-tailadmin.md`).

- `static/css/theme.css`: tokens da seção 3.2 em `:root`/`[data-bs-theme="light"]` e `[data-bs-theme="dark"]`, mapeados para as variáveis `--bs-*` do Bootstrap 5.3 (cores, fonte Outfit, raios de 8 e 16px). Ajusta botões, campos, cartões, tabelas, dropdown, toasts e modal do Bootstrap e define os componentes próprios.

  | Classe | Componente |
  |---|---|
  | `.page-head`, `.crumbs` | cabeçalho de página e trilha |
  | `.card-head`, `.card-foot` | cabeçalho e rodapé de cartão |
  | `.stat` | indicador |
  | `.pairs` | pares rótulo/valor |
  | `.linhas` / `.linha` | listas em cartão |
  | `.tag-*` | etiquetas |
  | `.avatar` | iniciais |
  | `.filters` | barra de filtros |
  | `.pager` | paginação |
  | `.empty` | estado vazio |
  | `.board`, `.board-col`, `.task-card` | quadro |
  | `.chat`, `.msg` | assistente |
  | `.auth` | entrar e criar conta |
  | `.erro-pagina` | erros |
  | `.table-cards` | tabela que vira cartões abaixo de 768px, com `data-label` em cada célula |

- `pages/templatetags/ui.py`: `{% icone %}`, `{% etiqueta_prioridade %}`, `{% etiqueta_estagio %}`, `{% etiqueta_papel %}`, `{% etiqueta_grupo %}`, `{% etiqueta_situacao %}` (mapeamento da seção 3.3 num só lugar), `{% avatar %}`, filtro `iniciais`, `{% trilha %}` e `{% paginas %}`.
- `templates/base.html`: Outfit e Bootstrap Icons 1.11.3 por CDN, tema claro como padrão e escuro só por escolha no botão do cabeçalho (salva em `localStorage`), barra lateral recolhível (`menu-recolhido`), cabeçalho com busca, tema e menu do usuário, link "Pular para o conteúdo". `templates/auth_base.html` é o layout dividido de entrar e criar conta; `erro_simples.html` serve 400 e 500.
- `templates/includes/`: `sidebar.html` (ícones e grupos), `messages.html` (toasts), `pagination.html` (numerada, sempre com `url_pagina`), `filtros.html` (recolhidos no celular), `lista_cabecalho.html`, `empty_state.html` e `avatar.html`.
- `static/js/app.js`: tema, menu (recolher no desktop, gaveta no celular), filtros no celular, Bootbox com ícone e botões do modal (seção 8) e as máscaras do jQuery Mask.
- Formulários continuam com crispy-forms + crispy-bootstrap5, em uma coluna dentro do cartão `.form-card` de até 720px.
- Apoio às telas: `Task.vencida` (prazo vencido no quadro e no detalhe) e o progresso dos projetos no painel (`annotate` em `HomeView`).

## 14. Decisões

| Data | Tela | Decisão | Motivo |
|---|---|---|---|
| 11/11/2026 | Layout base | Abordagem A: barra lateral fixa com grupos de menu e barra superior com busca e usuário | Comporta todos os menus, inclusive os de IA, e segue o padrão de painéis em Bootstrap. Protótipo em `prototypes/layout-base.html` |
| 11/11/2026 | Assistente de IA | Abordagem C: página de conversa com coluna de apoio (cota, perguntas frequentes e limites) | Atende à exigência de uma tela no visual do site e deixa o consumo e os limites visíveis. Protótipo em `prototypes/assistente.html` |
| 12/11/2026 | Quadro e formulários | Cartões do kanban também podem ser arrastados entre colunas (mantendo as setas); membros de equipe e de projeto passam a ser caixas de seleção em grade; tema claro como padrão | A lista de seleção múltipla exigia Ctrl para marcar mais de uma pessoa e parecia aceitar só uma; arrastar é o gesto esperado num quadro kanban |
| 11/11/2026 | Todas | Nova identidade inspirada no TailAdmin: paleta brand `#465FFF`, fonte Outfit, Bootstrap Icons, cartões de 16px, tabelas que viram cartões no celular e tema escuro com alternância. Mantém as abordagens A e C com o novo visual | A interface antiga do projeto (TailAdmin) era prática e agradável; a proposta única, aplicada a todas as telas, deixa o sistema mais limpo, consistente e responsivo. Protótipo em `prototypes/interface-tailadmin.html` (https://claude.ai/artifact/Qo296wGA8fiFjxLpa6wzMJ) |
