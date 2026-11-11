# Contexto do sistema Outsourcing

O Outsourcing é um sistema web de gestão de equipes, projetos e tarefas em quadro kanban. Toda a navegação fica no menu lateral, dividido em Trabalho, Gestão, Inteligência artificial e Sistema.

## Papéis

- **Administrador**: acesso total. Gerencia usuários e seus papéis (menu Usuários), equipes e a configuração da IA.
- **Gerente**: cria projetos nas equipes que gerencia e organiza os estágios desses projetos. Consulta as próprias equipes.
- **Desenvolvedor**: trabalha nas tarefas dos projetos em que participa.
- Quem cria uma conta pela tela "Criar conta" entra como Desenvolvedor. Só um administrador muda o papel de alguém.

## Conceitos e regras

- **Equipe**: tem um gerente e vários desenvolvedores. Só administradores cadastram, editam ou excluem equipes. Uma equipe com projetos não pode ser excluída.
- **Projeto**: pertence a uma equipe, tem início, término opcional e membros atribuídos, que precisam ser da equipe. O término não pode ser anterior ao início. Em "Meus projetos" cada gerente vê, edita e exclui só os projetos que ele mesmo cadastrou. Excluir um projeto apaga seus estágios e tarefas.
- **Estágio**: coluna do quadro. Todo projeto nasce com quatro estágios, nesta ordem: Backlog, Em andamento, Concluído e Aprovado. Gerentes e administradores podem criar outros em "Estágios". Um estágio com tarefas não pode ser excluído.
- **Tarefa**: tem título, descrição, estágio, responsável, prazo e prioridade (Baixa, Média, Alta ou Urgente). O responsável precisa ser o gerente da equipe ou um membro do projeto. Qualquer participante do projeto cria e edita tarefas no menu "Tarefas".
- **Anotação**: nota privada sobre uma tarefa, no menu "Minhas anotações". Só quem escreveu vê, edita ou exclui, nem administradores têm acesso.
- **Apontamento de horas**: registro privado das horas dedicadas a uma tarefa em uma data (de 0,25 a 24 horas), no menu "Meus apontamentos". Também é visível só para quem cadastrou.

## Como fazer

- **Ver o quadro**: menu "Quadros", depois o nome do projeto. Cada coluna é um estágio, e cada cartão mostra prioridade, responsável e prazo.
- **Mover uma tarefa**: no quadro, clique na seta ▶ do cartão para levar a tarefa ao próximo estágio, ou na seta ◀ para voltar ao anterior. Não há arrastar e soltar. A tarefa só se move entre estágios do mesmo projeto, e uma mensagem confirma a mudança.
- **Buscar e filtrar**: a busca da barra superior procura tarefas pelo título. As telas "Tarefas" e "Meus projetos" têm filtros, e a paginação mantém a busca.
- **Excluir um registro**: o botão Excluir pede confirmação em uma janela antes de apagar.
- **Anotar ou apontar horas**: abra a tarefa e use "Nova anotação" ou "Apontar horas".
- **Minha conta**: altere dados pessoais, perfil com redes sociais, endereço e senha.

## Assistente e consumo

- O assistente explica o uso do sistema. Ele não acessa os dados do usuário e não executa ações.
- Cada usuário tem uma cota mensal de tokens, mostrada em "Meu consumo" e ao lado da conversa. Ela renova no dia 1º de cada mês.
- O assistente considera só as últimas mensagens da conversa. "Limpar histórico" apaga a conversa.
