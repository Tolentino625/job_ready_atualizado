from datetime import date
from app.models.lembrete import Lembrete


class CriarLembreteService:
    def __init__(self, dados, usuario_id):
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        titulo = str(self.dados.get("titulo", "")).strip()
        descricao = self.dados.get("descricao")
        data_raw = self.dados.get("data")

        if not titulo or not data_raw:
            raise ValueError("Os campos 'titulo' e 'data' são obrigatórios.")

        try:
            data = date.fromisoformat(str(data_raw))
        except (TypeError, ValueError):
            raise ValueError("A data informada é inválida.")

        return Lembrete.criar(usuario_id=self.usuario_id, titulo=titulo, descricao=descricao, data=data)
