from app.models.pergunta import Pergunta


class BuscarPerguntaService:
    """Caso de uso: buscar uma pergunta pelo id, garantindo que pertence ao usuário."""

    def __init__(self, pergunta_id, usuario_id=None):
        self.pergunta_id = pergunta_id
        self.usuario_id = usuario_id

    def execute(self):
        pergunta = Pergunta.buscar_por_id(self.pergunta_id)
        if not pergunta:
            raise LookupError("Pergunta não encontrada.")
        if self.usuario_id is not None and pergunta.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para acessar esta pergunta.")
        return pergunta
