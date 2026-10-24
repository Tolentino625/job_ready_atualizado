from app.models.resposta import Resposta


class BuscarRespostaService:
    """Caso de uso: buscar uma resposta pelo id, garantindo que a entrevista pertence ao usuário."""

    def __init__(self, resposta_id, usuario_id=None):
        self.resposta_id = resposta_id
        self.usuario_id = usuario_id

    def execute(self):
        resposta = Resposta.buscar_por_id(self.resposta_id)
        if not resposta:
            raise LookupError("Resposta não encontrada.")
        if self.usuario_id is not None and (
            not resposta.entrevista or resposta.entrevista.usuario_id != self.usuario_id
        ):
            raise PermissionError("Você não tem permissão para acessar esta resposta.")
        return resposta
