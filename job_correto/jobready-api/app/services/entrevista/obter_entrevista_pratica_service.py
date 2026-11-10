from app.models.entrevista import Entrevista

TIPO_PRATICA = "pratica_perguntas"


class ObterEntrevistaPraticaService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        entrevista = (
            Entrevista.query
            .filter_by(usuario_id=self.usuario_id, tipo=TIPO_PRATICA)
            .order_by(Entrevista.id)
            .first()
        )
        if entrevista:
            return entrevista
        return Entrevista.criar(usuario_id=self.usuario_id, tipo=TIPO_PRATICA, status="em_andamento")
