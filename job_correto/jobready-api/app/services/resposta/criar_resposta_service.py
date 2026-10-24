from app.models.entrevista import Entrevista
from app.models.resposta import Resposta


class CriarRespostaService:
    """Caso de uso: registrar a resposta do usuário autenticado a uma pergunta."""

    def __init__(self, dados, usuario_id):
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        obrigatorios = ("entrevista_id", "pergunta_id", "texto_resposta")
        if not all(self.dados.get(campo) for campo in obrigatorios):
            raise ValueError(
                "Campos 'entrevista_id', 'pergunta_id' e 'texto_resposta' são obrigatórios."
            )

        entrevista = Entrevista.buscar_por_id(self.dados["entrevista_id"])
        if not entrevista:
            raise ValueError("A entrevista informada não existe.")
        if entrevista.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para responder nesta entrevista.")

        return Resposta.criar(
            entrevista_id=self.dados["entrevista_id"],
            pergunta_id=self.dados["pergunta_id"],
            texto_resposta=self.dados["texto_resposta"],
            tipo=self.dados.get("tipo", "texto"),
        )
