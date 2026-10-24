from app.services.resposta.buscar_resposta_service import BuscarRespostaService


class DeletarRespostaService:
    """Caso de uso: excluir uma resposta existente (do próprio usuário)."""

    def __init__(self, resposta_id, usuario_id):
        self.resposta_id = resposta_id
        self.usuario_id = usuario_id

    def execute(self):
        resposta = BuscarRespostaService(self.resposta_id, self.usuario_id).execute()
        resposta.deletar()
