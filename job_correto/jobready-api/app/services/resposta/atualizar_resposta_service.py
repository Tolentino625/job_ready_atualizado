from app.services.resposta.buscar_resposta_service import BuscarRespostaService


class AtualizarRespostaService:
    """Caso de uso: atualizar os dados de uma resposta existente (do próprio usuário)."""

    def __init__(self, resposta_id, dados, usuario_id):
        self.resposta_id = resposta_id
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        resposta = BuscarRespostaService(self.resposta_id, self.usuario_id).execute()
        return resposta.atualizar(
            texto_resposta=self.dados.get("texto_resposta"),
            tipo=self.dados.get("tipo"),
        )
