from braces.views import GroupRequiredMixin

from .constants import ADMINISTRADOR, GERENTE


class AcessoPorGrupoMixin(GroupRequiredMixin):
    """Anônimo vai para o login; usuário fora do grupo recebe 403."""

    raise_exception = True
    redirect_unauthenticated_users = True

    def check_membership(self, groups):
        # Reaproveita os grupos já em cache no usuário, evitando repetir a consulta no menu.
        user = self.request.user
        return user.is_superuser or bool(set(groups) & user.nomes_grupos)


class SomenteAdministradorMixin(AcessoPorGrupoMixin):
    group_required = [ADMINISTRADOR]


class AdministradorOuGerenteMixin(AcessoPorGrupoMixin):
    group_required = [ADMINISTRADOR, GERENTE]
