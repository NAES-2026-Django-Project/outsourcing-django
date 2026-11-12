"""Cria (ou remove) dados de demonstração: contas, equipe, projetos, tarefas, anotações e apontamentos.

Uso:
    python manage.py popular_demo            # cria ou completa os dados, sem duplicar
    python manage.py popular_demo --remover  # apaga tudo o que o comando criou

A senha das contas vem da variável DEMO_SENHA (no .env). Rodar de novo atualiza a senha.
"""
import os
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.constants import DESENVOLVEDOR, GERENTE
from accounts.models import User
from projects.models import Note, Priority, Project, StageType, Task, Team, TimeEntry

DOMINIO = '@outsourcing.test'
EQUIPE = 'Equipe Demonstração'

CONTAS = (
    # e-mail, nome, sobrenome, grupo
    (f'gerente{DOMINIO}', 'Gabriela', 'Gerente', GERENTE),
    (f'dev1{DOMINIO}', 'Diego', 'Desenvolvedor', DESENVOLVEDOR),
    (f'dev2{DOMINIO}', 'Daniela', 'Desenvolvedora', DESENVOLVEDOR),
)

PROJETOS = (
    {
        'nome': 'Portal do Cliente',
        'descricao': 'Área logada para clientes acompanharem pedidos, faturas e chamados.',
        'membros': ('dev1', 'dev2'),
        'tarefas': (
            # título, estágio, prioridade, responsável, prazo em dias
            ('Levantar requisitos com o cliente', StageType.APPROVED, Priority.HIGH, 'gerente', -10),
            ('Prototipar a tela de login', StageType.DONE, Priority.MEDIUM, 'dev2', -3),
            ('Implementar cadastro de clientes', StageType.DOING, Priority.HIGH, 'dev1', 4),
            ('Listar faturas em aberto', StageType.DOING, Priority.MEDIUM, 'dev2', 6),
            ('Corrigir envio de e-mail de recuperação', StageType.BACKLOG, Priority.URGENT, 'dev1', 1),
            ('Abrir chamado pelo portal', StageType.BACKLOG, Priority.LOW, None, 20),
        ),
    },
    {
        'nome': 'App de Entregas',
        'descricao': 'Aplicativo para entregadores registrarem coletas e entregas em tempo real.',
        'membros': ('dev1',),
        'tarefas': (
            ('Definir rotas da API de entregas', StageType.DONE, Priority.HIGH, 'dev1', -5),
            ('Tela de lista de coletas do dia', StageType.DOING, Priority.HIGH, 'dev1', 3),
            ('Registrar foto do comprovante', StageType.BACKLOG, Priority.MEDIUM, 'dev1', 10),
            ('Notificar o cliente ao sair para entrega', StageType.BACKLOG, Priority.URGENT, 'gerente', 2),
            ('Relatório de entregas por entregador', StageType.BACKLOG, Priority.LOW, None, 30),
            ('Revisar textos do aplicativo', StageType.APPROVED, Priority.LOW, 'gerente', -8),
        ),
    },
)

# Registros privados do dev1: (título da tarefa, conteúdo da anotação ou (horas, descrição) do apontamento)
ANOTACOES = (
    ('Implementar cadastro de clientes', 'Validar CPF e CNPJ no formulário antes de salvar.'),
    ('Corrigir envio de e-mail de recuperação', 'O link expira cedo demais; conferir o timeout do token.'),
)
APONTAMENTOS = (
    ('Implementar cadastro de clientes', Decimal('3.5'), 'Modelagem e formulário'),
    ('Tela de lista de coletas do dia', Decimal('2'), 'Layout da lista e filtros'),
    ('Definir rotas da API de entregas', Decimal('4'), 'Documentação das rotas'),
)


class Command(BaseCommand):
    help = 'Cria dados de demonstração (contas @outsourcing.test, equipe, projetos e tarefas) ou os remove com --remover.'

    def add_arguments(self, parser):
        parser.add_argument('--remover', action='store_true', help='Remove os dados de demonstração.')

    @transaction.atomic
    def handle(self, *args, remover=False, **options):
        if remover:
            self.remover()
            return
        senha = os.environ.get('DEMO_SENHA', '')
        if not senha:
            raise CommandError('Defina DEMO_SENHA no .env com a senha das contas de demonstração.')
        usuarios = self.criar_contas(senha)
        equipe = self.criar_equipe(usuarios)
        tarefas = {}
        for dados in PROJETOS:
            tarefas.update(self.criar_projeto(dados, equipe, usuarios))
        self.criar_registros_privados(usuarios['dev1'], tarefas)
        self.stdout.write(self.style.SUCCESS(
            f'Dados de demonstração prontos: {len(usuarios)} contas, {len(PROJETOS)} projetos, {len(tarefas)} tarefas.'
        ))

    def criar_contas(self, senha):
        usuarios = {}
        for email, nome, sobrenome, grupo in CONTAS:
            usuario, _ = User.objects.get_or_create(email=email, defaults={'first_name': nome, 'last_name': sobrenome})
            usuario.set_password(senha)
            usuario.save()
            usuario.groups.set([Group.objects.get(name=grupo)])
            usuarios[email.split('@')[0]] = usuario
        return usuarios

    def criar_equipe(self, usuarios):
        equipe, _ = Team.objects.get_or_create(name=EQUIPE, defaults={'manager': usuarios['gerente']})
        equipe.members.add(usuarios['dev1'], usuarios['dev2'])
        return equipe

    def criar_projeto(self, dados, equipe, usuarios):
        hoje = timezone.localdate()
        projeto, _ = Project.objects.get_or_create(
            name=dados['nome'], team=equipe,
            defaults={
                'description': dados['descricao'], 'created_by': usuarios['gerente'],
                'start_date': hoje - timedelta(days=30), 'end_date': hoje + timedelta(days=60),
            },
        )
        projeto.assigned_members.add(*(usuarios[apelido] for apelido in dados['membros']))
        estagios = {estagio.stage_type: estagio for estagio in projeto.stages.all()}
        tarefas = {}
        for titulo, tipo, prioridade, responsavel, prazo in dados['tarefas']:
            # Busca pelo título no projeto todo: uma tarefa movida no quadro não volta ao estágio original.
            tarefa = Task.objects.filter(title=titulo, stage__project=projeto).first()
            if tarefa is None:
                tarefa = Task(
                    title=titulo, stage=estagios[tipo], priority=prioridade,
                    assigned_to=usuarios.get(responsavel), due_date=hoje + timedelta(days=prazo),
                )
                tarefa.full_clean()
                tarefa.save()
            tarefas[titulo] = tarefa
        return tarefas

    def criar_registros_privados(self, autor, tarefas):
        for titulo, conteudo in ANOTACOES:
            Note.objects.get_or_create(task=tarefas[titulo], author=autor, defaults={'content': conteudo})
        for titulo, horas, descricao in APONTAMENTOS:
            TimeEntry.objects.get_or_create(
                task=tarefas[titulo], author=autor, description=descricao, defaults={'hours': horas},
            )

    def remover(self):
        usuarios = User.objects.filter(email__endswith=DOMINIO)
        equipes = Team.objects.filter(Q(name=EQUIPE) | Q(manager__in=usuarios))
        # Projetos protegem a equipe e o criador; excluí-los leva junto estágios, tarefas, anotações e apontamentos.
        Project.objects.filter(Q(team__in=equipes) | Q(created_by__in=usuarios)).delete()
        Team.objects.filter(pk__in=equipes.values('pk')).delete()
        usuarios.delete()
        self.stdout.write(self.style.SUCCESS('Dados de demonstração removidos.'))
