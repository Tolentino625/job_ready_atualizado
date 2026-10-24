from app.models.entrevista import Entrevista
from app.models.resposta import Resposta


class ObterRespostasUsuarioService:
    """Retorna um dicionário {pergunta_id: Resposta} com as respostas que o
    usuário autenticado já deu a perguntas do banco de perguntas. Usado para
    exibir na tela de Perguntas se cada uma já foi respondida e qual a nota
    da IA, sem expor o conceito de 'entrevista' ao usuário."""

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
