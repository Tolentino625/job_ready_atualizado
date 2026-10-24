from app.services.ia.gemini_client import extrair_json, gerar_conteudo
from app.services.resposta.buscar_resposta_service import BuscarRespostaService

_PROMPT_TEMPLATE = """Você é um recrutador(a) experiente avaliando a resposta de um \
candidato numa simulação de entrevista de emprego.

Pergunta feita ao candidato: {texto_pergunta}
Categoria: {categoria} | Dificuldade: {dificuldade}
{bloco_sugestao}
Resposta do candidato:
\"\"\"{texto_resposta}\"\"\"

Avalie a resposta do candidato considerando clareza, relevância para a \
pergunta e completude. Responda SOMENTE com um JSON válido, sem markdown, \
sem comentários e sem texto adicional, exatamente neste formato:
{{"nota": 0, "comentario": "feedback curto, direto e construtivo, em até 3 frases"}}
A nota deve ser um número de 0 a 10 (pode ter uma casa decimal)."""


class AvaliarRespostaService:
    """Caso de uso: pedir ao Gemini uma nota (0 a 10) e um comentário para
    a resposta do usuário autenticado a uma pergunta de entrevista."""

    def __init__(self, resposta_id, usuario_id):
        self.resposta_id = resposta_id
        self.usuario_id = usuario_id

    def execute(self):
        resposta = BuscarRespostaService(self.resposta_id, self.usuario_id).execute()
        pergunta = resposta.pergunta

        bloco_sugestao = ""
        if pergunta and pergunta.sugestao_resposta:
            bloco_sugestao = (
                "Sugestão de boa resposta, usada apenas como referência interna "
                f"(não mencione isso na resposta): {pergunta.sugestao_resposta}\n"
            )

        prompt = _PROMPT_TEMPLATE.format(
            texto_pergunta=pergunta.texto if pergunta else "(pergunta não encontrada)",
            categoria=pergunta.categoria if pergunta else "-",
            dificuldade=pergunta.dificuldade if pergunta else "-",
            bloco_sugestao=bloco_sugestao,
            texto_resposta=resposta.texto_resposta,
        )

        response = gerar_conteudo(prompt, temperature=0.3, max_output_tokens=500)

        try:
            avaliacao = extrair_json(response.text)
        except (ValueError, TypeError) as exc:
            raise RuntimeError(
                "O Gemini retornou uma resposta inválida ao avaliar sua resposta. Tente novamente."
            ) from exc

        if not isinstance(avaliacao, dict):
            raise RuntimeError("O Gemini não retornou uma avaliação válida.")

        try:
            nota = float(avaliacao.get("nota"))
        except (TypeError, ValueError) as exc:
            raise RuntimeError("O Gemini não retornou uma nota válida.") from exc
        nota = round(max(0.0, min(10.0, nota)), 1)

        comentario = str(avaliacao.get("comentario") or "").strip()
        if not comentario:
            raise RuntimeError("O Gemini não retornou um comentário para a avaliação.")

        return resposta.definir_avaliacao_ia(nota, comentario)
