"""Cria (ou remove) dados de demonstração: contas, equipes, projetos, tarefas, anotações e apontamentos.

Uso:
    python manage.py popular_demo            # cria ou completa os dados, sem duplicar
    python manage.py popular_demo --remover  # apaga tudo o que o comando criou

A senha das contas vem da variável DEMO_SENHA (no .env). Rodar de novo atualiza a senha.
A conta administradora padrão (--admin) é mantida no grupo Administrador e nunca é removida.
"""
import os
from datetime import timedelta
from decimal import Decimal
from itertools import cycle

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE
from accounts.models import User
from projects.models import Note, Priority, Project, StageType, Task, Team, TimeEntry

DOMINIO = '@outsourcing.test'
ADMIN_PADRAO = 'andreyviniciusjodar@gmail.com'

# apelido: (nome, sobrenome, grupo). O e-mail é <apelido>@outsourcing.test.
CONTAS = {
    'gerente.web': ('Gabriela', 'Moreira', GERENTE),
    'gerente.mobile': ('Marcelo', 'Teixeira', GERENTE),
    'ana': ('Ana', 'Souza', DESENVOLVEDOR),
    'bruno': ('Bruno', 'Lima', DESENVOLVEDOR),
    'carla': ('Carla', 'Mendes', DESENVOLVEDOR),
    'diego': ('Diego', 'Ferreira', DESENVOLVEDOR),
    'elisa': ('Elisa', 'Ramos', DESENVOLVEDOR),
    'fabio': ('Fábio', 'Costa', DESENVOLVEDOR),
}

# Cada equipe tem um gerente, três desenvolvedores e dois projetos. Carla também atua na equipe Mobile.
EQUIPES = (
    {
        'nome': 'Web', 'gerente': 'gerente.web', 'membros': ('ana', 'bruno', 'carla'),
        'projetos': (
            {
                'nome': 'Portal do Cliente',
                'descricao': 'Área logada para clientes acompanharem pedidos, faturas e chamados.',
                'devs': ('ana', 'bruno', 'carla'),
                'tarefas': (
                    'Tela de login com recuperação de senha', 'Cadastro de clientes',
                    'Listagem de faturas em aberto', 'Download da segunda via do boleto',
                    'Abertura de chamados pelo portal', 'Histórico de pedidos do cliente',
                    'Levantar requisitos com o cliente', 'Definir identidade visual do portal',
                ),
            },
            {
                'nome': 'Loja Virtual',
                'descricao': 'Catálogo de produtos com carrinho, pagamento e acompanhamento de entregas.',
                'devs': ('ana', 'bruno', 'carla'),
                'tarefas': (
                    'Catálogo com filtros por categoria', 'Página de detalhes do produto',
                    'Carrinho de compras', 'Cálculo de frete por CEP',
                    'Integração com o gateway de pagamento', 'E-mail de confirmação do pedido',
                    'Painel de vendas para o gerente', 'Política de trocas e devoluções',
                ),
            },
        ),
    },
    {
        'nome': 'Mobile', 'gerente': 'gerente.mobile', 'membros': ('diego', 'elisa', 'fabio', 'carla'),
        'projetos': (
            {
                'nome': 'App de Entregas',
                'descricao': 'Aplicativo para entregadores registrarem coletas e entregas em tempo real.',
                'devs': ('diego', 'elisa', 'fabio'),
                'tarefas': (
                    'Lista de coletas do dia', 'Rota otimizada no mapa',
                    'Foto do comprovante de entrega', 'Assinatura do recebedor na tela',
                    'Modo offline com sincronização', 'Notificar o cliente ao sair para entrega',
                    'Relatório de entregas por entregador', 'Revisar textos do aplicativo',
                ),
            },
            {
                'nome': 'App de Agendamentos',
                'descricao': 'Aplicativo para clientes marcarem horários em salões e clínicas parceiras.',
                'devs': ('diego', 'elisa', 'carla'),
                'tarefas': (
                    'Agenda semanal do profissional', 'Reserva de horário pelo cliente',
                    'Lembrete por notificação um dia antes', 'Cancelamento com antecedência mínima',
                    'Avaliação do atendimento', 'Cadastro de serviços e preços',
                    'Pesquisa com clientes piloto', 'Publicar versão beta nas lojas',
                ),
            },
        ),
    },
)

# Ordem dos estágios: cada desenvolvedor recebe duas tarefas em estágios diferentes.
ESTAGIOS = (StageType.BACKLOG, StageType.DOING, StageType.DONE, StageType.APPROVED)
PRAZO_POR_ESTAGIO = {StageType.BACKLOG: 12, StageType.DOING: 4, StageType.DONE: -3, StageType.APPROVED: -9}
PRIORIDADES = (Priority.HIGH, Priority.MEDIUM, Priority.URGENT, Priority.LOW)

# Duas anotações por projeto: (projeto, índice da tarefa, texto). O autor é o responsável pela tarefa.
ANOTACOES = (
    ('Portal do Cliente', 0, 'O token de recuperação expira em 15 minutos; confirmar o prazo com o cliente.'),
    ('Portal do Cliente', 3, 'O banco devolve o PDF em base64; salvar em cache por um dia.'),
    ('Loja Virtual', 1, 'Fotos do produto em 3 tamanhos para não pesar no celular.'),
    ('Loja Virtual', 4, 'Usar o ambiente de testes do gateway até a homologação.'),
    ('App de Entregas', 2, 'Comprimir a foto antes de enviar; a rede dos entregadores é lenta.'),
    ('App de Entregas', 5, 'Mensagem curta, com link de rastreio e previsão de chegada.'),
    ('App de Agendamentos', 0, 'Mostrar a semana a partir de segunda e destacar o dia atual.'),
    ('App de Agendamentos', 3, 'Antecedência mínima de 2 horas, configurável por parceiro.'),
)
HORAS = (Decimal('2'), Decimal('3.5'), Decimal('1.5'))
APONTAMENTO = 'Desenvolvimento e testes'


class Command(BaseCommand):
    help = (
        'Cria dados de demonstração (contas @outsourcing.test, duas equipes, quatro projetos e tarefas) '
        'ou os remove com --remover.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--remover', action='store_true', help='Remove os dados de demonstração.')
        parser.add_argument(
            '--admin', default=ADMIN_PADRAO,
            help=f'E-mail da conta mantida no grupo Administrador (padrão: {ADMIN_PADRAO}).',
        )

    @transaction.atomic
    def handle(self, *args, remover=False, admin=ADMIN_PADRAO, **options):
        if remover:
            self.remover()
            return
        senha = os.environ.get('DEMO_SENHA', '')
        if not senha:
            raise CommandError('Defina DEMO_SENHA no .env com a senha das contas de demonstração.')
        self.manter_administrador(admin)
        usuarios = self.criar_contas(senha)
        tarefas_por_projeto = {}
        for dados_equipe in EQUIPES:
            equipe = self.criar_equipe(dados_equipe, usuarios)
            for dados_projeto in dados_equipe['projetos']:
                tarefas_por_projeto[dados_projeto['nome']] = self.criar_projeto(
                    dados_projeto, equipe, usuarios, giro=len(tarefas_por_projeto),
                )
        self.criar_registros_privados(usuarios, tarefas_por_projeto)
        total_tarefas = sum(len(tarefas) for tarefas in tarefas_por_projeto.values())
        self.stdout.write(self.style.SUCCESS(
            f'Dados de demonstração prontos: {len(usuarios)} contas, {len(EQUIPES)} equipes, '
            f'{len(tarefas_por_projeto)} projetos e {total_tarefas} tarefas.'
        ))

    def manter_administrador(self, email):
        usuario = User.objects.filter(email__iexact=email).first()
        if usuario is None:
            self.stdout.write(self.style.WARNING(f'Conta administradora {email} não encontrada; nada alterado nela.'))
            return
        usuario.groups.add(Group.objects.get(name=ADMINISTRADOR))
        if not usuario.is_staff:
            usuario.is_staff = True
            usuario.save(update_fields=['is_staff'])

    def criar_contas(self, senha):
        usuarios = {}
        for apelido, (nome, sobrenome, grupo) in CONTAS.items():
            usuario, _ = User.objects.get_or_create(
                email=f'{apelido}{DOMINIO}', defaults={'first_name': nome, 'last_name': sobrenome},
            )
            usuario.set_password(senha)
            usuario.save()
            usuario.groups.set([Group.objects.get(name=grupo)])
            usuarios[apelido] = usuario
        return usuarios

    def criar_equipe(self, dados, usuarios):
        equipe, _ = Team.objects.get_or_create(name=dados['nome'], defaults={'manager': usuarios[dados['gerente']]})
        equipe.members.add(*(usuarios[apelido] for apelido in dados['membros']))
        return equipe

    def criar_projeto(self, dados, equipe, usuarios, giro=0):
        hoje = timezone.localdate()
        projeto, _ = Project.objects.get_or_create(
            name=dados['nome'], team=equipe,
            defaults={
                'description': dados['descricao'], 'created_by': equipe.manager,
                'start_date': hoje - timedelta(days=30), 'end_date': hoje + timedelta(days=90),
            },
        )
        devs = [usuarios[apelido] for apelido in dados['devs']]
        projeto.assigned_members.add(*devs)
        estagios = {estagio.stage_type: estagio for estagio in projeto.stages.all()}

        # Dois títulos por desenvolvedor, em estágios diferentes; os dois últimos ficam
        # sem responsável (backlog) e com o gerente (em andamento).
        responsaveis = [dev for dev in devs for _ in range(2)] + [None, equipe.manager]
        # O giro muda o estágio inicial a cada projeto, variando quem tem tarefas concluídas e aprovadas.
        giro %= len(ESTAGIOS)
        tipos = cycle(ESTAGIOS[giro:] + ESTAGIOS[:giro])
        tipos_por_tarefa = [next(tipos) for _ in range(len(devs) * 2)] + [StageType.BACKLOG, StageType.DOING]
        prioridades = cycle(PRIORIDADES)

        tarefas = []
        for titulo, responsavel, tipo in zip(dados['tarefas'], responsaveis, tipos_por_tarefa):
            # Busca pelo título no projeto todo: uma tarefa movida no quadro não volta ao estágio original.
            tarefa = Task.objects.filter(title=titulo, stage__project=projeto).first()
            if tarefa is None:
                tarefa = Task(
                    title=titulo, stage=estagios[tipo], priority=next(prioridades), assigned_to=responsavel,
                    due_date=hoje + timedelta(days=PRAZO_POR_ESTAGIO[tipo]),
                )
                tarefa.full_clean()
                tarefa.save()
            tarefas.append(tarefa)
        return tarefas

    def criar_registros_privados(self, usuarios, tarefas_por_projeto):
        for nome_projeto, indice, texto in ANOTACOES:
            tarefa = tarefas_por_projeto[nome_projeto][indice]
            autor = tarefa.assigned_to or tarefa.stage.project.created_by
            Note.objects.get_or_create(task=tarefa, content=texto, defaults={'author': autor})
        # Um apontamento por desenvolvedor, na primeira tarefa dele que não está no backlog.
        todas = [tarefa for tarefas in tarefas_por_projeto.values() for tarefa in tarefas]
        desenvolvedores = [usuarios[a] for a, (_, _, grupo) in CONTAS.items() if grupo == DESENVOLVEDOR]
        for horas, dev in zip(cycle(HORAS), desenvolvedores):
            if TimeEntry.objects.filter(author=dev, description=APONTAMENTO).exists():
                continue  # já criado numa execução anterior, mesmo que as tarefas tenham sido movidas
            tarefa = next(
                (t for t in todas if t.assigned_to_id == dev.pk and t.stage.stage_type != StageType.BACKLOG), None,
            )
            if tarefa:
                TimeEntry.objects.create(task=tarefa, author=dev, description=APONTAMENTO, hours=horas)

    def remover(self):
        usuarios = User.objects.filter(email__endswith=DOMINIO)
        equipes = Team.objects.filter(manager__in=usuarios)
        # Projetos protegem a equipe e o criador; excluí-los leva junto estágios, tarefas, anotações e apontamentos.
        Project.objects.filter(Q(team__in=equipes) | Q(created_by__in=usuarios)).delete()
        Team.objects.filter(pk__in=equipes.values('pk')).delete()
        usuarios.delete()
        self.stdout.write(self.style.SUCCESS('Dados de demonstração removidos.'))
