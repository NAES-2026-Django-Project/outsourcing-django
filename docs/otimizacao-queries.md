# Otimização de queries

Critérios T2-2.4, T2-2.5 e T3-1.1. O Django Debug Toolbar fica ativo com `DEBUG=True`; abra o painel **SQL** em qualquer tela para ver as consultas e as duplicadas.

## Medição

Banco com 30 tarefas, 30 projetos e 30 usuários, acessado como gerente. "Sem otimização" desativa `select_related` e `prefetch_related` durante a medição. "Repetidas" conta as execuções além da primeira de uma mesma SQL idêntica.

| Tela | Queries sem otimização | Repetidas | Queries otimizadas | Repetidas |
|---|---|---|---|---|
| Tarefas | 37 | 18 | 7 | 0 |
| Meus projetos | 16 | 9 | 6 | 0 |
| Estágios | 15 | 7 | 5 | 0 |
| Anotações | 15 | 0 | 5 | 0 |
| Apontamentos | 36 | 15 | 6 | 0 |
| Quadros | 15 | 9 | 5 | 0 |
| Quadro do projeto | 47 | 7 | 7 | 0 |
| Início | 23 | 9 | 8 | 0 |

## O que foi feito

- `select_related` nas listas e detalhes: `stage__project` e `assigned_to` em tarefas, `team` e `created_by` em projetos, `project` em estágios, `manager` em equipes, `task__stage__project` em anotações e apontamentos.
- `prefetch_related` em relações múltiplas: `tasks__assigned_to` no quadro e no estágio, `members` e `projects` na equipe, `groups` na lista de usuários.
- `Count` e `Sum` no banco para totais, sem carregar os registros.
- Grupos do usuário em cache (`User.nomes_grupos`), reaproveitados pelo menu e pelo `AcessoPorGrupoMixin`. A medição apontou essa consulta duplicada em todas as telas protegidas por grupo.

## Proteção contra regressão

`QueriesTests` em `projects/tests.py` verifica que o número de queries das listas, do quadro e do início não cresce com o número de registros.
