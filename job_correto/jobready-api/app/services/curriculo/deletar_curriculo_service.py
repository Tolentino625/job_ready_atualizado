from app.services.curriculo.arquivo_service import apagar_arquivo
from app.services.curriculo.buscar_curriculo_service import BuscarCurriculoService


class DeletarCurriculoService:
    """Caso de uso: excluir currículo (do próprio usuário) e seu anexo."""

    def __init__(self, curriculo_id, usuario_id):
        self.curriculo_id = curriculo_id
        self.usuario_id = usuario_id

    def execute(self):
        curriculo = BuscarCurriculoService(self.curriculo_id, self.usuario_id).execute()
        arquivo = curriculo.arquivo_path
        curriculo.deletar()
        apagar_arquivo(arquivo)
