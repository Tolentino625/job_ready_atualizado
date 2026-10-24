from app.models.entrevista import Entrevista
from app.models.feedback import Feedback


class CriarFeedbackService:
    """Caso de uso: registrar o feedback de desempenho de uma entrevista do usuário autenticado."""

    def __init__(self, dados, usuario_id):
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        if not self.dados.get("entrevista_id") or self.dados.get("pontuacao") is None:
            raise ValueError("Campos 'entrevista_id' e 'pontuacao' são obrigatórios.")

        entrevista = Entrevista.buscar_por_id(self.dados["entrevista_id"])
        if not entrevista:
            raise ValueError("A entrevista informada não existe.")
        if entrevista.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para criar feedback nesta entrevista.")

        return Feedback.criar(
            entrevista_id=self.dados["entrevista_id"],
            pontuacao=self.dados["pontuacao"],
            comentario=self.dados.get("comentario"),
            ponto_forte=self.dados.get("ponto_forte"),
            ponto_a_melhorar=self.dados.get("ponto_a_melhorar"),
        )
