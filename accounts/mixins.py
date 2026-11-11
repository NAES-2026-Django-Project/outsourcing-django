from braces.views import GroupRequiredMixin

from .constants import ADMINISTRADOR, GERENTE


class AcessoPorGrupoMixin(GroupRequiredMixin):
    """Anônimo vai para o login; usuário fora do grupo recebe 403."""

    raise_exception = True
    redirect_unauthenticated_users = True


class SomenteAdministradorMixin(AcessoPorGrupoMixin):
    group_required = [ADMINISTRADOR]


class AdministradorOuGerenteMixin(AcessoPorGrupoMixin):
    group_required = [ADMINISTRADOR, GERENTE]
