from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_pagina(context, pagina):
    """Monta o link de uma página mantendo os parâmetros atuais da busca."""
    parametros = context['request'].GET.copy()
    parametros['page'] = pagina
    return f'?{parametros.urlencode()}'
