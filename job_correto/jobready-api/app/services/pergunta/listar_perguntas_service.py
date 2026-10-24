from app.models.pergunta import Pergunta


class ListarPerguntasService:
    """Caso de uso: listar as perguntas geradas pelo usuário autenticado."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Pergunta.listar_por_usuario(self.usuario_id)
