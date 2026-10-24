from app.services.entrevista.buscar_entrevista_service import BuscarEntrevistaService


class DeletarEntrevistaService:
    """Caso de uso: excluir uma entrevista existente (do próprio usuário)."""

    def __init__(self, entrevista_id, usuario_id):
        self.entrevista_id = entrevista_id
        self.usuario_id = usuario_id

    def execute(self):
        entrevista = BuscarEntrevistaService(self.entrevista_id, self.usuario_id).execute()
        entrevista.deletar()
