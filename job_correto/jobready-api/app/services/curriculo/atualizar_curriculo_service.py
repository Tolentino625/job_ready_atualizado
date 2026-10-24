from app.services.curriculo.arquivo_service import apagar_arquivo, salvar_arquivo
from app.services.curriculo.buscar_curriculo_service import BuscarCurriculoService


class AtualizarCurriculoService:
    """Caso de uso: atualizar currículo (do próprio usuário) e substituir o anexo quando enviado."""

    def __init__(self, curriculo_id, dados, arquivo, usuario_id):
        self.curriculo_id = curriculo_id
        self.dados = dados or {}
        self.arquivo = arquivo
        self.usuario_id = usuario_id

    def execute(self):
        curriculo = BuscarCurriculoService(self.curriculo_id, self.usuario_id).execute()
        arquivo_info = salvar_arquivo(self.arquivo) if self.arquivo else None
        antigo = curriculo.arquivo_path
        # A nota da IA só vale para o conteúdo que foi avaliado: se o anexo ou
        # o texto do currículo mudarem, ela é descartada (precisa reavaliar).
        novo_texto = self.dados.get("conteudo_texto")
        conteudo_mudou = bool(arquivo_info) or (
            novo_texto is not None and (novo_texto or "") != (curriculo.conteudo_texto or "")
        )
        try:
            atualizado = curriculo.atualizar(
                nome_arquivo=arquivo_info["nome_arquivo"] if arquivo_info else self.dados.get("nome_arquivo"),
                conteudo_texto=self.dados.get("conteudo_texto"),
                pontos_fortes=self.dados.get("pontos_fortes"),
                pontos_a_melhorar=self.dados.get("pontos_a_melhorar"),
                arquivo_path=arquivo_info["arquivo_path"] if arquivo_info else None,
                arquivo_mimetype=arquivo_info["arquivo_mimetype"] if arquivo_info else None,
            )
            if conteudo_mudou and atualizado.nota_ia is not None:
                atualizado.invalidar_nota()
            if arquivo_info and antigo:
                apagar_arquivo(antigo)
            return atualizado
        except Exception:
            if arquivo_info:
                apagar_arquivo(arquivo_info["arquivo_path"])
            raise
