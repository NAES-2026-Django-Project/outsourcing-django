# Escopo herdado do projeto antigo

Resumo de `../outsourcing-deprecated/outsourcing-backend` (API DRF). Serve para orientar o domínio; a arquitetura antiga não é reaproveitada. O frontend Angular só tinha login e cadastro sobre o template TailAdmin, sem telas de domínio.

## Entidades

Cadeia principal: Team → Project → Stage → Task → Note. Todas tinham `created_at`, `updated_at` e `is_active`.

| Entidade | Campos | Relações |
|---|---|---|
| User | e-mail como login, `first_name`, `last_name`, `phone`, papel | |
| Profile | URLs de instagram, facebook, linkedin, twitter | 1:1 User |
| Address | `country`, `state`, `city`, `cep` | 1:1 User |
| Team | `name` (único) | `manager` FK User; `members` M2M User |
| Project | `name`, `description`, `start_date`, `end_date` | `team` FK; `assigned_members` M2M User |
| Stage | `name`, `stage_type` (backlog, doing, done, approved), `order` | `project` FK; único por (project, order) |
| Task | `title`, `description`, `due_date`, `priority` (low, medium, high, urgent) | `stage` FK PROTECT; `assigned_to` FK User opcional |
| Note | `content` | `task` FK; `author` FK User |

## Regras de negócio a manter

- Criar usuário cria Profile e Address.
- Criar projeto cria quatro estágios: Backlog, In Progress, Done, Approved.
- Task: o estágio deve estar ativo; o responsável deve ser o gerente da equipe ou membro atribuído ao projeto.
- Project: `end_date` não pode ser anterior a `start_date`; a equipe deve estar ativa; membros atribuídos devem pertencer à equipe; gerente só cria projetos nas equipes que gerencia.
- Stage: só administrador ou gerente escrevem; `stage_type` e `project` são imutáveis; estágio com tarefas ativas não pode ser excluído.
- Team: só administrador escreve; o gerente deve ter papel de gerente; membros devem ser desenvolvedores ativos.
- Somente administrador altera o papel de um usuário; e-mail não muda após a criação.

## Permissões por papel

- **Administrador**: acesso total.
- **Gerente**: suas equipes (leitura), projetos e estágios dessas equipes (escrita), tarefas e notas de seus projetos.
- **Desenvolvedor**: equipes e projetos em que participa (leitura); cria e edita tarefas e notas nos projetos atribuídos.

## Falhas do legado a corrigir

- Cadastro público aceitava `role`, permitindo se registrar como administrador.
- Mover tarefa não verificava se o estágio destino era do mesmo projeto.

## Mudanças decididas para o monolito

- Papéis viram Groups do Django.
- `Project` e `Note` ganham posse estrita por usuário (critério T3-1.3). Notas passam a ser anotações privadas do autor.
- Movimento de tarefa ganha view própria (`TaskMoveView`).
- Exclusão física no lugar do `is_active`, atendendo ao `DeleteView` do critério. Só `User.is_active` permanece.
