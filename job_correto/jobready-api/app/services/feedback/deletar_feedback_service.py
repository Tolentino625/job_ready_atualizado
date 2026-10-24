from app.services.feedback.buscar_feedback_service import BuscarFeedbackService


class DeletarFeedbackService:
    """Caso de uso: excluir um feedback existente (do próprio usuário)."""

    def __init__(self, feedback_id, usuario_id):
        self.feedback_id = feedback_id
        self.usuario_id = usuario_id

    def execute(self):
        feedback = BuscarFeedbackService(self.feedback_id, self.usuario_id).execute()
        feedback.deletar()
