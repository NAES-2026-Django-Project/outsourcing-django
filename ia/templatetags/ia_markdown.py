from django import template
from django.utils.safestring import mark_safe

from ia.markdown import markdown_seguro as converter

register = template.Library()


@register.filter
def markdown_seguro(texto):
    return mark_safe(converter(texto))  # noqa: S308 - HTML já sanitizado pelo nh3
