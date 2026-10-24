from app.models.entrevista import Entrevista
from app.services.simulacao.comum import TIPO_SIMULACAO


class ListarSimulacoesService:
    """Caso de uso: histórico de simulações cronometradas do usuário (mais recentes primeiro)."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        entrevistas = (
            Entrevista.query.filter_by(usuario_id=self.usuario_id, tipo=TIPO_SIMULACAO)
            .order_by(Entrevista.id.desc())
            .all()
        )
        return [
            {**e.to_dict(), "total": len(e.simulacao_itens),
             "respondidas": sum(1 for i in e.simulacao_itens if i.respondida)}
            for e in entrevistas
        ]
