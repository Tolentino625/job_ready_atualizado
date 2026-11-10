from app.models.entrevista import Entrevista


class CriarEntrevistaService:

    def __init__(self, dados, usuario_id):
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        return Entrevista.criar(
            usuario_id=self.usuario_id,
            tipo=self.dados.get("tipo", "texto"),
            status=self.dados.get("status", "em_andamento"),
            pontuacao_geral=self.dados.get("pontuacao_geral"),
        )
