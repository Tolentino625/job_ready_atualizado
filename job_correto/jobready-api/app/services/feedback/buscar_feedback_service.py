from app.models.feedback import Feedback


class BuscarFeedbackService:
    """Caso de uso: buscar um feedback pelo id, garantindo que a entrevista pertence ao usuário."""

    def __init__(self, feedback_id, usuario_id=None):
        self.feedback_id = feedback_id
        self.usuario_id = usuario_id

    def execute(self):
        feedback = Feedback.buscar_por_id(self.feedback_id)
        if not feedback:
            raise LookupError("Feedback não encontrado.")
        if self.usuario_id is not None and (
            not feedback.entrevista or feedback.entrevista.usuario_id != self.usuario_id
        ):
            raise PermissionError("Você não tem permissão para acessar este feedback.")
        return feedback
