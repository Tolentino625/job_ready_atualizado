from app.models.usuario import Usuario
from app.services.usuario.buscar_usuario_service import BuscarUsuarioService


class AtualizarUsuarioService:
    """Caso de uso: atualizar os dados do próprio usuário autenticado."""

    def __init__(self, usuario_id, dados, usuario_atual_id):
        self.usuario_id = usuario_id
        self.dados = dados or {}
        self.usuario_atual_id = usuario_atual_id

    def execute(self):
        usuario = BuscarUsuarioService(self.usuario_id, self.usuario_atual_id).execute()
        email = self.dados.get("email")
        if email and email.strip().lower() != usuario.email:
            outro = Usuario.buscar_por_email(email)
            if outro and outro.id != usuario.id:
                raise ValueError("Já existe um usuário com este e-mail.")
        senha = self.dados.get("senha")
        if senha is not None and senha != "" and len(senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        return usuario.atualizar(
            nome=self.dados.get("nome"),
            email=email,
            senha=senha,
        )
