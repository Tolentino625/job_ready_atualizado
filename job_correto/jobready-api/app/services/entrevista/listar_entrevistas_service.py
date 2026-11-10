from app.models.entrevista import Entrevista


class ListarEntrevistasService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Entrevista.listar_por_usuario(self.usuario_id)
