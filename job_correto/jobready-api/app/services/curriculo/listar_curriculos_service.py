from app.models.curriculo import Curriculo


class ListarCurriculosService:
    """Caso de uso: listar os currículos do usuário autenticado."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Curriculo.listar_por_usuario(self.usuario_id)
