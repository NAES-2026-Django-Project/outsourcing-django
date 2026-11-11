import markdown as md
import nh3

TAGS_PERMITIDAS = {
    'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote', 'ul', 'ol', 'li',
    'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a', 'hr',
}


def markdown_seguro(texto):
    """Converte Markdown em HTML e remove tudo que não estiver na lista de tags permitidas."""
    html = md.markdown(texto or '', extensions=['fenced_code', 'tables', 'sane_lists'])
    return nh3.clean(
        html,
        tags=TAGS_PERMITIDAS,
        attributes={'a': {'href', 'title'}},
        url_schemes={'http', 'https', 'mailto'},
        link_rel='noopener noreferrer',
    )
