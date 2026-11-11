"""Única porta de entrada para a IA. Nenhum outro módulo chama a API do Gemini."""

import time

from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from google import genai
from google.genai import errors, types

from .models import ChamadaIA, ConfiguracaoIA, CotaUsuario, MensagemAssistente, Origem, Papel, Status

JANELA_MENSAGENS = 5
CONTEXTO_PROJETO = settings.BASE_DIR / 'contexto_projeto.md'
TIMEOUT_MS = 60_000
# Motivos de término em que o Gemini bloqueia a resposta por política de conteúdo.
MOTIVOS_DE_BLOQUEIO = {'SAFETY', 'PROHIBITED_CONTENT', 'BLOCKLIST', 'SPII', 'RECITATION', 'IMAGE_SAFETY'}


class ErroIA(Exception):
    """Falha com mensagem pronta para mostrar ao usuário."""


class CotaExcedida(ErroIA):
    pass


def criar_cliente(chave):
    return genai.Client(api_key=chave, http_options=types.HttpOptions(timeout=TIMEOUT_MS))


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
    if isinstance(erro, errors.APIError):
        texto = f'{erro.status or ""} {erro.message or ""}'
        if erro.code in (401, 403) or 'API_KEY_INVALID' in texto or 'API key' in texto:
            return 'A chave da API foi recusada. Peça ao administrador para revisar a configuração.'
        if erro.code == 404:
            return 'O modelo configurado não foi encontrado.'
        if erro.code == 429:
            return 'O limite gratuito da API do Gemini foi atingido. Tente novamente em instantes.'
        return f'A API respondeu com erro {erro.code}. Tente novamente mais tarde.'
    return 'Não foi possível conectar à API do Gemini. Tente novamente mais tarde.'


def _nome(valor):
    return getattr(valor, 'name', valor) or ''


def _para_conteudos(mensagens):
    """Converte o histórico (papéis user/assistant) no formato do Gemini (user/model)."""
    return [
        {'role': 'user' if m['role'] == Papel.USUARIO else 'model', 'parts': [{'text': m['content']}]}
        for m in mensagens
    ]


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

    configuracao = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=config.max_tokens,
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel[config.esforco.upper()]),
    )
    inicio = time.monotonic()
    # O cliente precisa continuar referenciado durante a chamada: ao ser descartado, ele fecha a conexão.
    cliente = criar_cliente(chave)
    try:
        resposta = cliente.models.generate_content(
            model=config.modelo, contents=_para_conteudos(mensagens), config=configuracao,
        )
    except Exception as erro:  # noqa: BLE001 - toda falha precisa ser auditada antes de chegar ao usuário
        chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
        _falhar(chamada, Status.ERRO, _mensagem_de_erro(erro), detalhe=f'{type(erro).__name__}: {erro}')
    finally:
        cliente.close()
    chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)

    uso = resposta.usage_metadata
    if uso:
        chamada.tokens_entrada = uso.prompt_token_count or 0
        chamada.tokens_saida = (uso.candidates_token_count or 0) + (uso.thoughts_token_count or 0)

    bloqueio_da_pergunta = _nome(getattr(resposta.prompt_feedback, 'block_reason', None))
    candidato = resposta.candidates[0] if resposta.candidates else None
    motivo = _nome(candidato.finish_reason) if candidato else ''
    if bloqueio_da_pergunta or motivo in MOTIVOS_DE_BLOQUEIO:
        _falhar(
            chamada, Status.RECUSADA, 'O assistente não pode responder a essa pergunta.',
            detalhe=f'bloqueio={bloqueio_da_pergunta or motivo}',
        )
    partes = (candidato.content.parts or []) if candidato and candidato.content else []
    chamada.resposta = ''.join(p.text for p in partes if p.text and not p.thought).strip()
    if motivo == 'MAX_TOKENS':
        chamada.resposta += '\n\n_(Resposta interrompida pelo limite de tokens.)_'
    if not chamada.resposta:
        _falhar(chamada, Status.ERRO, 'O assistente não retornou uma resposta. Tente novamente.', detalhe=f'finish_reason={motivo}')
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
    cliente = criar_cliente(chave)
    try:
        modelo = cliente.models.get(model=config.modelo)
    except Exception as erro:  # noqa: BLE001
        chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
        chamada.status, chamada.erro = Status.ERRO, f'{type(erro).__name__}: {erro}'[:2000]
        chamada.save()
        return False, _mensagem_de_erro(erro)
    finally:
        cliente.close()
    nome = modelo.display_name or config.modelo
    chamada.duracao_ms = int((time.monotonic() - inicio) * 1000)
    chamada.status = Status.SUCESSO
    chamada.resposta = f'Modelo disponível: {nome}'
    chamada.save()
    return True, f'Conexão bem-sucedida. Modelo disponível: {nome}.'


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
