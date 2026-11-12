# Nova interface inspirada no TailAdmin: DESIGN.md e protótipo clicável

- Status: em andamento
- Critérios: T3-2.5 (reforço), DEF-4, T1-1.5
- Entrada: protótipo clicável de todas as interfaces, inspirado no TailAdmin, e DESIGN.md reformulado

## Contexto

O sistema funciona e cumpre 50 dos 51 critérios. A interface atual (Bootstrap 5 + `static/css/theme.css`, azul-petróleo, sem ícones) é funcional, mas tem pontos fracos:

- **Hierarquia visual pouco clara:** títulos, cartões e tabelas têm o mesmo peso.
- **Botões sem ícones e espaçamento irregular:** as ações ficam difíceis de achar.
- **Responsividade básica:** quadro e tabelas ficam apertados no celular.

O desenvolvedor quer refatorar a aparência inspirado no **TailAdmin**, a biblioteca do frontend antigo (`outsourcing-deprecated/outsourcing-frontend/src/styles.css`). Ele **não** quer comparar três opções: quer uma proposta única, aplicada a **todas** as telas atuais.

Decisões do desenvolvedor:

- **Identidade:** paleta do TailAdmin (brand `#465FFF`, cinzas frios, sucesso, erro e aviso) e fonte **Outfit**.
- **Ícones:** **Bootstrap Icons**. No protótipo, vão em SVG embutido, porque os artifacts bloqueiam CDN de CSS e fontes.
- **Entrega desta rodada:** **DESIGN.md reescrito + protótipo clicável publicado como Claude artifact.** Os templates Django serão refatorados num plano seguinte, depois da aprovação do protótipo.

Referências extraídas do TailAdmin para seguir de perto:

- **Barra lateral:** branca, de 290px, com borda à direita e grupos de menu em maiúsculas cinza. Itens de 14px com ícone de 24px; o item ativo fica com fundo `brand-50` e texto `brand-500`.
- **Cabeçalho:** branco, fixo no topo, com borda inferior.
- **Cartões:** `rounded-2xl` (16px), com borda `gray-200`, cabeçalho de 20px por 24px de padding e corpo separado por uma borda `gray-100`.
- **Tabelas:** cabeçalho em `gray-500` de 12px, linhas separadas por `gray-100`.
- **Etiquetas:** em formato de pílula, com fundo suave e texto forte (por exemplo, `success-50` com `success-600`).
- **Sombras:** `theme-xs` e `theme-sm`. Escala de texto de 12/18, 14/20 e 20/30.

## 1. Revisão de configurações e ambiente

- [x] O inventário das telas atuais saiu de `templates/` e dos `urls.py` (lista na seção 2).
- [x] Tokens do TailAdmin lidos em `src/styles.css`: brand, gray, success, error, warning, blue-light, sombras e escala de texto.
- [ ] Ler os tópicos `pages` e `design` do guia de artifacts antes de publicar.
- Nenhuma dependência nova no Django nesta rodada. O Bootstrap Icons via CDN e a fonte Outfit (Google Fonts) ficam registrados no DESIGN.md para a implementação.

## 2. Etapas e commits

Branch: `docs/design-tailadmin`.

### A. Reescrever `docs/design/DESIGN.md`
- [ ] `docs(design): reescrever a identidade visual inspirada no TailAdmin`

Seções do novo DESIGN.md:

1. **Princípios:** clareza, consistência, densidade confortável, ação primária evidente, acessibilidade (contraste AA, foco visível) e responsividade, tudo com exemplos do sistema.
2. **Inspiração TailAdmin:** o que foi adotado (estrutura, tokens, componentes) e o que foi adaptado ao Bootstrap 5.
3. **Tokens de cor:** escalas brand, gray, success, error, warning e info, nos temas claro e escuro, com o uso semântico de cada uma e o mapeamento para `--bs-*`.
4. **Tipografia:** Outfit com fallback de sistema, escala de títulos (30/38, 24/32, 20/30, 16/24), texto (14/20, 12/18) e números tabulares.
5. **Espaçamento, raio e sombra:**
   - grade de 4px;
   - raio de 8px em controles, 16px em cartões e pílula em etiquetas;
   - sombras `xs`, `sm` e `md`.
6. **Layout:**
   - barra lateral de 290px, recolhível em telas largas e em gaveta abaixo de 992px;
   - cabeçalho fixo de 64px;
   - conteúdo com padding de 24/16px e largura máxima de 1440px.
7. **Responsividade:** pontos de quebra do Bootstrap e comportamento por componente:
   - tabelas viram listas de cartões abaixo de 768px;
   - o kanban rola na horizontal com *snap*;
   - formulários em uma coluna.
8. **Componentes, com anatomia e estados:**
   - ações: botões (primário, secundário, perigo, só ícone);
   - formulários: campos (altura de 44px, foco com anel `brand-500/10`, erro), seleção, área de texto e caixa de seleção;
   - indicadores: etiquetas (status, prioridade, papel, situação da IA) e cartão de indicador;
   - estrutura: cartão, cabeçalho de página com trilha de navegação, tabela, barra de filtros e paginação;
   - estados: estado vazio, toast e modal de confirmação;
   - telas específicas: cartão do kanban, balões do chat e barra de progresso de cota.
9. **Padrões de tela:**
   - painel;
   - lista (com filtros);
   - detalhe (resumo + seções);
   - formulário;
   - quadro;
   - conversa;
   - erro;
   - autenticação.
10. **Ícones:** tabela com o Bootstrap Icon de cada item de menu e de cada ação.
11. **Textos da interface:** verbos nos botões, mensagens das ações, estados vazios com o próximo passo.
12. **Acessibilidade:** contraste, foco, `aria-label` nos botões de ícone, alvos de toque de 44px e navegação por teclado.
13. **Implementação no Django:** como os tokens viram variáveis em `static/css/theme.css`, quais classes do Bootstrap reaproveitar e o que muda em `base.html` e `includes/`.
14. **Decisões:** mantém o histórico e adiciona a linha de 11/11/2026 sobre a adoção do TailAdmin. O layout com barra lateral (A) e o assistente com coluna de apoio (C) continuam valendo, com o novo visual.

### B. Protótipo clicável com todas as telas
- [ ] `docs(design): protótipo clicável da nova interface`

Arquivo: `docs/design/prototypes/interface-tailadmin.html`, publicado como Claude artifact.

Como ele é feito:

- Um só HTML com CSS e JS embutidos, sem CDN, porque a política do artifact bloqueia.
- Navegação por hash, com cada tela desenhada a partir de dados de exemplo iguais aos do `popular_demo` (equipes Web e Mobile, os 4 projetos, Ana, Bruno, Carla...).
- Fonte Outfit declarada, com fallback de sistema.
- Ícones do Bootstrap Icons em SVG embutido.

Telas, todas as interfaces atuais:

| Grupo | Telas |
|---|---|
| Público | Início para visitante, Entrar, Criar conta, Sobre (texto e diagramas como figuras), erros 403, 404 e 500 |
| Trabalho | Início (painel com indicadores, tarefas e projetos recentes); Quadros (lista); Quadro kanban; Tarefas (lista com filtros e paginação); Detalhe da tarefa (com anotações e apontamentos); Nova e editar tarefa; Minhas anotações (lista, detalhe, formulário); Meus apontamentos (lista com total de horas, detalhe, formulário) |
| Gestão | Meus projetos (lista com filtros, detalhe, formulário); Estágios (lista, detalhe, formulário); Equipes (lista, detalhe, formulário); Usuários (lista e troca de papel) |
| IA | Assistente (conversa com coluna de apoio); Meu consumo; Configuração da IA (com Testar conexão); Requisições (lista com filtros e detalhe); IA por usuário e Editar cota |
| Conta | Minha conta, Dados, Perfil, Endereço, Alterar senha |

Interações funcionando:

- **Navegação:** menu lateral com item ativo e grupos visíveis conforme o papel. Um seletor de papel na própria demonstração (Administrador, Gerente, Desenvolvedor) mostra o que cada um vê.
- **Kanban:** mover a tarefa com ◀ ▶ e "+" por coluna que abre o formulário no estágio certo.
- **Ações:** salvar e excluir com toast; exclusão com modal de confirmação no estilo Bootbox.
- **Listas e formulários:** filtros e busca funcionando nas listas; validação visual nos formulários.
- **Assistente:** pergunta com resposta simulada em Markdown e barra de cota.
- **Tema e menu:** alternância entre tema claro e escuro; barra lateral recolhível no desktop e em gaveta com fundo escurecido no celular.

### C. Registro
- [ ] Atualizar a linha de decisão no DESIGN.md com o link do artifact. Salvar este plano em `docs/plans/2026-11-11-interface-tailadmin.md`, com `docs(plans): planejar a nova interface`.

## 3. Revisão de escopo (verificação do protótipo)

Não há código Django nesta rodada, então a prova é no navegador:

- Abrir o artifact publicado no painel do navegador e percorrer **todas** as rotas da tabela. Cada uma deve renderizar sem erro no console (conferido com `read_console_messages`).
- Testar em **375px** (celular), **768px** (tablet) e **1280px** (desktop):
  - a barra lateral vira gaveta;
  - as tabelas viram cartões;
  - o kanban rola na horizontal;
  - nada transborda (`document.documentElement.scrollWidth <= innerWidth`).
- **Tema escuro:** conferir o contraste dos textos principais e das etiquetas.
- **Papéis:** o desenvolvedor não vê Gestão nem as telas administrativas de IA; o gerente vê Gestão, mas não Usuários.
- **Fluxos:** mover uma tarefa até "Aprovado", criar tarefa pelo "+", excluir com confirmação, filtrar tarefas, enviar uma pergunta ao assistente.
- **Coerência:** cada tela do protótipo existe no sistema atual, e nenhuma funcionalidade nova é inventada.

## 4. Adequação ao critério avaliativo

- **T3-2.5 (interface amigável e navegação coerente):** reforçado, com a proposta documentada e prototipada. Fica como base para a refatoração dos templates.
- **DEF-4 e T1-1.5 (layout com framework front-end):** continuam no Bootstrap 5. O DESIGN.md documenta como os tokens do TailAdmin sobrescrevem o Bootstrap, sem trocar de framework.
- Nenhum critério muda de estado nesta rodada. Na implementação, rodar `/validate-criterion` em DEF-4, DEF-7, T1-1.5, T3-1.5 e T3-2.5.

## Arquivos

- `docs/design/DESIGN.md`, reescrito.
- `docs/design/prototypes/interface-tailadmin.html`, novo; os protótipos antigos ficam como histórico.
- `docs/plans/2026-11-11-interface-tailadmin.md`.
- Consultados:
  - `outsourcing-deprecated/outsourcing-frontend/src/styles.css`;
  - os componentes de layout, cartão e tabela do TailAdmin em `src/app/shared/`;
  - todos os `templates/` atuais;
  - `static/css/theme.css`;
  - `projects/management/commands/popular_demo.py`, para os dados de exemplo.
