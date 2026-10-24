from app.models.entrevista import Entrevista


class BuscarEntrevistaService:
    """Caso de uso: buscar uma entrevista pelo id, garantindo que pertence ao usuário."""

    def __init__(self, entrevista_id, usuario_id=None):
        self.entrevista_id = entrevista_id
        self.usuario_id = usuario_id

    def execute(self):
        entrevista = Entrevista.buscar_por_id(self.entrevista_id)
        if not entrevista:
            raise LookupError("Entrevista não encontrada.")
        if self.usuario_id is not None and entrevista.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para acessar esta entrevista.")
        return entrevista
