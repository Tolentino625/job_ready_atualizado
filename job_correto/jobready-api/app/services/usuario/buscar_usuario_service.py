from app.models.usuario import Usuario


class BuscarUsuarioService:
    """Caso de uso: buscar um usuário pelo id, garantindo que é o próprio usuário autenticado."""

    def __init__(self, usuario_id, usuario_atual_id=None):
        self.usuario_id = usuario_id
        self.usuario_atual_id = usuario_atual_id

    def execute(self):
        usuario = Usuario.buscar_por_id(self.usuario_id)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        if self.usuario_atual_id is not None and usuario.id != self.usuario_atual_id:
            raise PermissionError("Você só pode acessar os seus próprios dados.")
        return usuario
