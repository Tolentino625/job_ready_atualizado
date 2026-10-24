from google.genai import types

from app.services.curriculo.arquivo_service import uploads_dir
from app.services.curriculo.buscar_curriculo_service import BuscarCurriculoService
from app.services.ia.gemini_client import extrair_json, gerar_conteudo

# Tipos de arquivo que o Gemini consegue "ler" diretamente (multimodal).
_MIME_MULTIMODAL_SUPORTADOS = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/heic",
}

_PROMPT_INSTRUCOES = """Você é um recrutador(a) sênior, especialista em análise de \
currículos para o mercado de trabalho brasileiro.

Analise o currículo enviado a seguir (pode vir como texto e/ou como um \
arquivo anexo) e devolva uma avaliação estruturada e prática, pensada para \
ajudar o candidato a melhorar o documento antes de se candidatar a vagas.

Dê uma nota geral de 0 a 10 (pode ter uma casa decimal), considerando: clareza \
e organização, objetividade, relevância e resultados na experiência, formação e \
habilidades, e ausência de erros de escrita. Seja criterioso e realista: reserve \
notas acima de 8 para currículos realmente bons e use notas baixas quando o \
documento for vazio, confuso ou incompleto.

Responda SOMENTE com um JSON válido, sem markdown, sem comentários e sem \
texto adicional, exatamente neste formato:
{"nota": 0,
"pontos_fortes": "texto corrido com os principais pontos fortes do currículo",
"pontos_a_melhorar": "texto corrido com sugestões objetivas e acionáveis de melhoria",
"comentario_geral": "um parágrafo curto com a impressão geral e a justificativa da nota"}"""


class AvaliarCurriculoService:
    """Caso de uso: pedir ao Gemini uma avaliação do currículo e salvar a
    nota (0 a 10) e o feedback (pontos fortes / pontos a melhorar) no próprio registro."""

    def __init__(self, curriculo_id, usuario_id):
        self.curriculo_id = curriculo_id
        self.usuario_id = usuario_id

    def execute(self):
        curriculo = BuscarCurriculoService(self.curriculo_id, self.usuario_id).execute()

        conteudo = [_PROMPT_INSTRUCOES] + self._montar_partes_conteudo(curriculo)
        response = gerar_conteudo(conteudo, temperature=0.4, max_output_tokens=2000)

        try:
            avaliacao = extrair_json(response.text)
        except (ValueError, TypeError) as exc:
            raise RuntimeError(
                "O Gemini retornou uma resposta inválida ao avaliar o currículo. Tente novamente."
            ) from exc

        if not isinstance(avaliacao, dict):
            raise RuntimeError("O Gemini não retornou uma avaliação válida.")

        try:
            nota = round(max(0.0, min(10.0, float(avaliacao.get("nota")))), 1)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("O Gemini não retornou uma nota válida. Tente novamente.") from exc

        pontos_fortes = str(avaliacao.get("pontos_fortes") or "").strip()
        pontos_a_melhorar = str(avaliacao.get("pontos_a_melhorar") or "").strip()
        comentario_geral = str(avaliacao.get("comentario_geral") or "").strip()

        if not pontos_fortes and not pontos_a_melhorar:
            raise RuntimeError("O Gemini não conseguiu gerar uma avaliação para este currículo.")

        if comentario_geral:
            pontos_a_melhorar = (
                f"{pontos_a_melhorar}\n\nAvaliação geral: {comentario_geral}".strip()
            )

        return curriculo.definir_avaliacao_ia(nota, pontos_fortes, pontos_a_melhorar)

    def _montar_partes_conteudo(self, curriculo):
        """Monta as partes (texto e/ou arquivo) que serão enviadas ao Gemini."""
        partes = []

        if curriculo.conteudo_texto and curriculo.conteudo_texto.strip():
            partes.append(
                "Conteúdo do currículo (texto informado pelo usuário):\n"
                f"{curriculo.conteudo_texto.strip()}"
            )

        if curriculo.arquivo_path:
            caminho = self._resolver_caminho_arquivo(curriculo.arquivo_path)
            mimetype = curriculo.arquivo_mimetype or ""

            if caminho is None or not caminho.is_file():
                pass  # arquivo referenciado no banco não existe mais em disco
            elif mimetype == "text/plain":
                try:
                    texto_arquivo = caminho.read_text(encoding="utf-8", errors="ignore")
                    if texto_arquivo.strip():
                        partes.append(
                            "Conteúdo do arquivo de texto anexado:\n"
                            f"{texto_arquivo.strip()}"
                        )
                except OSError:
                    pass
            elif mimetype in _MIME_MULTIMODAL_SUPORTADOS:
                partes.append(
                    types.Part.from_bytes(data=caminho.read_bytes(), mime_type=mimetype)
                )
            elif not partes:
                # Formatos como .doc/.docx/.rtf/.odt não podem ser lidos
                # diretamente pelo Gemini nesta versão do serviço.
                raise ValueError(
                    f"O arquivo anexado ({mimetype or 'formato desconhecido'}) não pode "
                    "ser analisado diretamente pela IA. Envie o currículo em PDF, imagem "
                    "ou preencha o campo 'Conteúdo extraído / observações' com o texto "
                    "do currículo antes de avaliar."
                )

        if not partes:
            raise ValueError(
                "Este currículo não tem texto nem um anexo compatível para análise. "
                "Preencha o campo 'Conteúdo extraído / observações' ou envie um PDF/imagem."
            )

        return partes

    @staticmethod
    def _resolver_caminho_arquivo(arquivo_path):
        base = uploads_dir().parent.parent.resolve()
        caminho = (base / arquivo_path).resolve()
        try:
            caminho.relative_to(base)
        except ValueError:
            return None
        return caminho
