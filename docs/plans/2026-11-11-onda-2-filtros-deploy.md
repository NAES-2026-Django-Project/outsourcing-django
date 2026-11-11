# Onda 2: filtros, otimização, jQuery e deploy

- Status: em andamento
- Critérios: DEF-7, DEF-8, T2-2.4, T2-2.5, T3-1.1, T3-1.2, T3-1.5, T3-1.6
- Entrada: etapas 9 a 12 do plano geral aprovado

## 1. Revisão de configurações e ambiente

- [x] `django-filter` e `django-debug-toolbar` instalados e em `INSTALLED_APPS`
- [x] Banco Neon conectado e migrado
- [x] PostgreSQL local descartável para testes
- [ ] Google Cloud CLI instalada e projeto criado (ação do desenvolvedor)

## 2. Etapas e commits

### Filtros e paginação
- [x] `feat(projects): adicionar filtros em projetos e tarefas`
- [x] `feat(projects): preservar busca na paginação com templatetag`
- [x] `feat(pages): adicionar busca de tarefas na barra superior`

### Otimização
- [x] `perf(accounts): reaproveitar grupos em cache no controle de acesso`
- [x] `docs(projects): registrar medição de queries`

### jQuery
- [x] `feat(pages): confirmar exclusões com Bootbox`
- [x] `feat(accounts): adicionar máscaras de telefone e CEP`

### Deploy
- [x] `build(deploy): preparar publicação no App Engine`

### Testes
- [x] `test(projects): cobrir filtros, paginação e queries`

## 3. Revisão de escopo por testes

- [x] Filtros restringem os resultados e respeitam a visibilidade do usuário
- [x] Links de paginação preservam os parâmetros da busca
- [x] Número de queries das listas não cresce com o número de registros
- [x] Páginas carregam jQuery, Bootbox e Mask sem erros no navegador
- [x] Exclusão por Bootbox remove o registro e exibe a mensagem
- [x] Aplicação sobe com gunicorn e `DEBUG=False`

## 4. Adequação ao critério avaliativo

- [x] Validação registrada em `docs/criterios.md`
- [ ] T3-1.6: publicar com `gcloud app deploy` e registrar o link (ação do desenvolvedor)
