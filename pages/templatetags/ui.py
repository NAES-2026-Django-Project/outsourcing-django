"""Componentes de interface do DESIGN.md (seções 3.3 e 10): ícones, etiquetas e iniciais."""
from django import template
from django.utils.html import format_html

from accounts.constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE

register = template.Library()

CORES_PRIORIDADE = {'low': 'gray', 'medium': 'info', 'high': 'warning', 'urgent': 'error'}
CORES_ESTAGIO = {'backlog': 'gray', 'doing': 'brand', 'done': 'success', 'approved': 'success'}
CORES_PAPEL = {ADMINISTRADOR: 'brand', GERENTE: 'info', DESENVOLVEDOR: 'gray'}
CORES_SITUACAO = {'sucesso': 'success', 'erro': 'error', 'recusada': 'warning', 'bloqueada': 'gray'}


def _etiqueta(texto, cor, ponto=True):
    classe = 'tag tag-{}' if ponto else 'tag tag-{} sem-ponto'
    return format_html('<span class="' + classe + '">{}</span>', cor, texto)


@register.simple_tag
def icone(nome, classe=''):
    """Ícone decorativo do Bootstrap Icons."""
    return format_html('<i class="bi bi-{} {}" aria-hidden="true"></i>', nome, classe)


@register.simple_tag
def etiqueta_prioridade(tarefa):
    return _etiqueta(tarefa.get_priority_display(), CORES_PRIORIDADE.get(tarefa.priority, 'gray'))


@register.simple_tag
def etiqueta_estagio(estagio):
    return _etiqueta(estagio.name, CORES_ESTAGIO.get(estagio.stage_type, 'gray'))


@register.simple_tag
def etiqueta_papel(usuario):
    return _etiqueta(usuario.papel, CORES_PAPEL.get(usuario.papel, 'gray'), ponto=False)


@register.simple_tag
def etiqueta_situacao(chamada):
    return _etiqueta(chamada.get_status_display(), CORES_SITUACAO.get(chamada.status, 'gray'))


@register.filter
def iniciais(usuario):
    if not usuario:
        return '—'
    texto = f'{usuario.first_name[:1]}{usuario.last_name[:1]}'.upper()
    return texto or usuario.email[:1].upper()


@register.inclusion_tag('includes/avatar.html')
def avatar(usuario, tamanho=''):
    return {'usuario': usuario, 'tamanho': tamanho}


@register.simple_tag
def trilha(*partes, atual=''):
    """Trilha de navegação: pares de (nome de URL ou caminho, rótulo), começando sempre em Início."""
    from django.urls import NoReverseMatch, reverse

    itens = [('/', 'Início')]
    for destino, rotulo in zip(partes[::2], partes[1::2]):
        try:
            url = reverse(destino)
        except NoReverseMatch:
            url = destino
        itens.append((url, rotulo))
    links = format_html('').join(
        format_html('<a href="{}">{}</a><span aria-hidden="true">/</span>', url, rotulo) for url, rotulo in itens
    )
    return format_html('<nav class="crumbs" aria-label="Trilha">{}<span>{}</span></nav>', links, atual)


@register.simple_tag
def paginas(page_obj):
    """Números de página com reticências, centrados na página atual."""
    return list(page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1))


@register.simple_tag
def etiqueta_grupo(nome):
    """Etiqueta de papel a partir do nome do grupo (usa os grupos já carregados, sem nova consulta)."""
    return _etiqueta(nome, CORES_PAPEL.get(nome, 'gray'), ponto=False)
