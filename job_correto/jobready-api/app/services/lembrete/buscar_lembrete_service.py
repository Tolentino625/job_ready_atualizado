from app.models.lembrete import Lembrete


class BuscarLembreteService:
    """Caso de uso: buscar um lembrete pelo id, garantindo que pertence ao usuário."""

    def __init__(self, lembrete_id, usuario_id=None):
        self.lembrete_id = lembrete_id
        self.usuario_id = usuario_id

    def execute(self):
        lembrete = Lembrete.buscar_por_id(self.lembrete_id)
        if not lembrete:
            raise LookupError("Lembrete não encontrado.")
        if self.usuario_id is not None and lembrete.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para acessar este lembrete.")
        return lembrete
