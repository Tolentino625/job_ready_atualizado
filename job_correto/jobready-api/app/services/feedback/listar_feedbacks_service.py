from app.models.feedback import Feedback


class ListarFeedbacksService:
    """Caso de uso: listar os feedbacks das entrevistas do usuário autenticado."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Feedback.listar_por_usuario(self.usuario_id)
