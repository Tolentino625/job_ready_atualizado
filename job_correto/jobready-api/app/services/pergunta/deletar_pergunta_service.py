from app.services.pergunta.buscar_pergunta_service import BuscarPerguntaService


class DeletarPerguntaService:
    """Caso de uso: excluir uma pergunta do próprio usuário."""

    def __init__(self, pergunta_id, usuario_id):
        self.pergunta_id = pergunta_id
        self.usuario_id = usuario_id

    def execute(self):
        pergunta = BuscarPerguntaService(self.pergunta_id, self.usuario_id).execute()
        pergunta.deletar()
