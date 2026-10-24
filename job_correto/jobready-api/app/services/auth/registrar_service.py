from app.models.usuario import Usuario


class RegistrarUsuarioService:
    """Caso de uso: registrar uma conta para acesso ao JobReady."""

    def __init__(self, dados):
        self.dados = dados or {}

    def execute(self):
        nome = (self.dados.get("nome") or "").strip()
        email = (self.dados.get("email") or "").strip().lower()
        senha = self.dados.get("senha") or ""

        if not nome or not email or not senha:
            raise ValueError("Nome, e-mail e senha são obrigatórios.")
        if len(senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        if Usuario.buscar_por_email(email):
            raise ValueError("Já existe um usuário com este e-mail.")

        return Usuario.criar(nome=nome, email=email, senha=senha)
