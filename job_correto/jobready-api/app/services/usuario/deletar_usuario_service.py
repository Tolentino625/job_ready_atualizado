from app.services.usuario.buscar_usuario_service import BuscarUsuarioService


class DeletarUsuarioService:
    """Caso de uso: excluir o próprio usuário autenticado."""

    def __init__(self, usuario_id, usuario_atual_id):
        self.usuario_id = usuario_id
        self.usuario_atual_id = usuario_atual_id

    def execute(self):
        usuario = BuscarUsuarioService(self.usuario_id, self.usuario_atual_id).execute()
        usuario.deletar()
