from app.models.resposta import Resposta


class ListarRespostasService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Resposta.listar_por_usuario(self.usuario_id)
