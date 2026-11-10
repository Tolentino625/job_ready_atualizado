from app.models.entrevista import Entrevista
from app.models.resposta import Resposta


class ObterRespostasUsuarioService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        respostas = (
            Resposta.query
            .join(Entrevista, Resposta.entrevista_id == Entrevista.id)
            .filter(Entrevista.usuario_id == self.usuario_id)
            .all()
        )
        return {r.pergunta_id: r for r in respostas}
