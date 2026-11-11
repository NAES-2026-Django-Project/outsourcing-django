# Onda 1: núcleo do sistema

- Status: em andamento
- Critérios: DEF-1 a DEF-6, T1-1.2 a T1-1.7, T1-2.1 a T1-2.6, T2-1.1 a T2-1.9, T2-2.1 a T2-2.3, T3-1.3, T3-1.4
- Entrada: etapas 4 a 8 do plano geral aprovado

## 1. Revisão de configurações e ambiente

- [x] Dependências instaladas na `.venv` (`requirements.txt`)
- [x] Layout base escolhido (abordagem A, barra lateral)
- [x] PostgreSQL local descartável para testes, sem SQLite
- [ ] `.env` com `SECRET_KEY` e `DATABASE_URL` do Neon (ação do desenvolvedor)
- [x] `AUTH_USER_MODEL` definido antes do primeiro `migrate`

## 2. Etapas e commits

### Contas
- [x] `feat(accounts): adicionar usuário por e-mail, perfil e endereço`
- [x] `feat(accounts): criar grupos por migration de dados`
- [x] `feat(accounts): adicionar login, logout, cadastro e troca de senha`
- [x] `feat(accounts): adicionar telas de conta e gestão de usuários`

### Domínio
- [x] `feat(projects): adicionar models de equipes, projetos, estágios, tarefas e anotações`

### Layout e páginas
- [x] `feat(pages): adicionar layout base com barra lateral`
- [x] `feat(pages): adicionar início e página sobre com diagramas`

### CRUD
- [x] `feat(projects): adicionar CRUD com posse e controle por grupos`

### Movimento
- [x] `feat(projects): adicionar quadro kanban e movimentação de tarefas`

## 3. Revisão de escopo por testes

Rodar com `python manage.py test`.

- [x] Cadastro público sempre entra como Desenvolvedor, sem escolha de grupo
- [x] Anônimo é redirecionado ao login; grupo errado recebe 403
- [x] `Project` e `Note`: não dono recebe 404 em detalhe, edição e exclusão, e não vê na lista
- [x] `form_valid()` grava o dono
- [x] Criar projeto gera quatro estágios
- [x] Regras: datas do projeto, responsável da tarefa, estágio com tarefas não é excluído
- [x] Mover tarefa: sucesso, estágio de outro projeto recusado, não participante recebe 404
- [x] Mensagens em cadastro, alteração e exclusão

## 4. Adequação ao critério avaliativo

- [x] Validação dos critérios registrada em `docs/criterios.md`
- [ ] T3-1.3 pendente de decisão: `Project` aparece no quadro para os participantes
