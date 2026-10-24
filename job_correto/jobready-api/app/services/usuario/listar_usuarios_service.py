from app.models.usuario import Usuario


class ListarUsuariosService:
    """Caso de uso: listar usuários. Cada usuário só enxerga o próprio cadastro."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        usuario = Usuario.buscar_por_id(self.usuario_id)
        return [usuario] if usuario else []
