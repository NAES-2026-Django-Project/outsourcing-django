"""Única porta de entrada para a IA. Nenhum outro módulo chama a API da Anthropic."""

import time

import anthropic
from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .models import ChamadaIA, ConfiguracaoIA, CotaUsuario, MensagemAssistente, Origem, Papel, Status

JANELA_MENSAGENS = 5
CONTEXTO_PROJETO = settings.BASE_DIR / 'contexto_projeto.md'
# Modelos que aceitam o fallback de recusa no servidor com `fallbacks: "default"`.
MODELOS_COM_FALLBACK = {'claude-opus-5-5', 'claude-sonnet-5-5'}


class ErroIA(Exception):
    """Falha com mensagem pronta para mostrar ao usuário."""


class CotaExcedida(ErroIA):
    pass


def criar_cliente(chave):
    return anthropic.Anthropic(api_key=chave, timeout=60.0, max_retries=2)


def inicio_do_mes():
    return timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def consumo_mensal(usuario):
    total = ChamadaIA.objects.filter(usuario=usuario, criado_em__gte=inicio_do_mes()).aggregate(
        total=Sum(F('tokens_entrada') + F('tokens_saida')),
    )['total']
    return total or 0


def limite_mensal(usuario, config=None):
    limite = CotaUsuario.objects.filter(usuario=usuario).values_list('limite_mensal', flat=True).first()
    if limite is not None:
        return limite
    return (config or ConfiguracaoIA.carregar()).cota_mensal_padrao


def _falhar(chamada, status, mensagem, detalhe='', excecao=ErroIA):
    chamada.status = status
    chamada.erro = (detalhe or mensagem)[:2000]
    chamada.save()
    raise excecao(mensagem)


def _mensagem_de_erro(erro):
    if isinstance(erro, anthropic.AuthenticationError):
        return 'A chave da API foi recusada. Peça ao administrador para revisar a configuração.'
    if isinstance(erro, anthropic.PermissionDeniedError):
        return 'A chave da API não tem permissão para este modelo.'
    if isinstance(erro, anthropic.NotFoundError):
        return 'O modelo configurado não foi encontrado.'
    if isinstance(erro, anthropic.RateLimitError):
        return 'A API está recebendo muitas requisições. Tente novamente em instantes.'
    if isinstance(erro, anthropic.APIStatusError):
        return f'A API respondeu com erro {erro.status_code}. Tente novamente mais tarde.'
    return 'Não foi possível conectar à API da Anthropic. Tente novamente mais tarde.'


def chamar_ia(usuario, mensagens, origem, system=None):
    """Envia mensagens à IA, aplicando configuração, cota e auditoria. Retorna a ChamadaIA salva."""
    config = ConfiguracaoIA.carregar()
    chamada = ChamadaIA(
        usuario=usuario, origem=origem, modelo=config.modelo,
        pergunta=mensagens[-1]['content'] if mensagens else '',
    )
    if not config.ativo:
        _falhar(chamada, Status.ERRO, 'O assistente está desativado pelo administrador.')
    chave = config.obter_chave()
    if not chave:
        _falhar(chamada, Status.ERRO, 'A IA ainda não foi configurada pelo administrador.')
    if consumo_mensal(usuario) >= limite_mensal(usuario, config):
        _falhar(
            chamada, Status.BLOQUEADA,
            'Você atingiu sua cota mensal de tokens. Ela renova no dia 1º do próximo mês.',
            excecao=CotaExcedida,
        )

    parametros = {
        'model': config.modelo,
        'max_tokens': config.max_tokens,
        'messages': mensagens,
        'output_config': {'effort': config.esforco},
    }
    if system:
        parametros['system'] = system
    if config.modelo in MODELOS_COM_FALLBACK:
        parametros['betas'] = ['server-side-fallback-2026-07-01']
        parametros['fallbacks'] = 'default'

    inicio = time.monotonic()
    try:
        resposta = criar_cliente(chave).beta.messages.create(**parametros)
    except anthropic.APIError as erro:
        chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
        _falhar(chamada, Status.ERRO, _mensagem_de_erro(erro), detalhe=f'{type(erro).__name__}: {erro}')
    chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)

    uso = resposta.usage
    chamada.tokens_entrada = (
        (uso.input_tokens or 0)
        + (getattr(uso, 'cache_creation_input_tokens', 0) or 0)
        + (getattr(uso, 'cache_read_input_tokens', 0) or 0)
    )
    chamada.tokens_saida = uso.output_tokens or 0
    chamada.resposta = ''.join(bloco.text for bloco in resposta.content if bloco.type == 'text').strip()

    if resposta.stop_reason == 'refusal':
        _falhar(chamada, Status.RECUSADA, 'O assistente não pode responder a essa pergunta.', detalhe='stop_reason=refusal')
    if resposta.stop_reason == 'max_tokens':
        chamada.resposta += '\n\n_(Resposta interrompida pelo limite de tokens.)_'
    chamada.status = Status.SUCESSO
    chamada.save()
    return chamada


def testar_conexao(usuario):
    """Confere chave e modelo sem gastar tokens. Retorna (sucesso, mensagem) e audita o teste."""
    config = ConfiguracaoIA.carregar()
    chamada = ChamadaIA(usuario=usuario, origem=Origem.TESTE, modelo=config.modelo, pergunta='Testar conexão')
    chave = config.obter_chave()
    if not chave:
        chamada.status, chamada.erro = Status.ERRO, 'Nenhuma chave cadastrada.'
        chamada.save()
        return False, 'Cadastre uma chave da API antes de testar.'
    inicio = time.monotonic()
    try:
        modelo = criar_cliente(chave).models.retrieve(config.modelo)
    except anthropic.APIError as erro:
        chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
        chamada.status, chamada.erro = Status.ERRO, f'{type(erro).__name__}: {erro}'[:2000]
        chamada.save()
        return False, _mensagem_de_erro(erro)
    chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
    chamada.status = Status.SUCESSO
    chamada.resposta = f'Modelo disponível: {modelo.display_name}'
    chamada.save()
    return True, f'Conexão bem-sucedida. Modelo disponível: {modelo.display_name}.'


def montar_system(config):
    contexto = CONTEXTO_PROJETO.read_text(encoding='utf-8')
    return f'{config.instrucoes}\n\n<contexto_do_sistema>\n{contexto}\n</contexto_do_sistema>'


def janela_de_mensagens(usuario, pergunta):
    """Últimas mensagens do histórico mais a pergunta nova, no máximo JANELA_MENSAGENS, começando pelo usuário."""
    anteriores = MensagemAssistente.objects.filter(usuario=usuario).order_by('-criado_em', '-id')[:JANELA_MENSAGENS - 1]
    janela = [{'role': m.papel, 'content': m.conteudo} for m in reversed(anteriores)]
    janela.append({'role': Papel.USUARIO, 'content': pergunta})
    while janela[0]['role'] != Papel.USUARIO:
        janela.pop(0)
    return janela


def perguntar_ao_assistente(usuario, pergunta):
    """Envia a pergunta com a janela de contexto e grava as duas mensagens só quando a IA responde."""
    config = ConfiguracaoIA.carregar()
    chamada = chamar_ia(
        usuario, janela_de_mensagens(usuario, pergunta), Origem.ASSISTENTE, system=montar_system(config),
    )
    with transaction.atomic():
        MensagemAssistente.objects.create(usuario=usuario, papel=Papel.USUARIO, conteudo=pergunta)
        MensagemAssistente.objects.create(usuario=usuario, papel=Papel.ASSISTENTE, conteudo=chamada.resposta)
    return chamada.resposta
