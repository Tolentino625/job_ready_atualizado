from app.models.entrevista import Entrevista


class ListarEntrevistasService:
    """Caso de uso: listar as entrevistas do usuário autenticado."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Entrevista.listar_por_usuario(self.usuario_id)
