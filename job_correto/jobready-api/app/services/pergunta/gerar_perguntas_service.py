import json

from app.models.pergunta import ORIGEM_BANCO, Pergunta
from app.services.ia.gemini_client import extrair_json, gerar_conteudo

# Rótulo por extenso de cada área/categoria, usado no prompt para o Gemini
# entender melhor o contexto (em vez de receber só o slug, ex: "ti_programacao").
CATEGORIAS = {
    "comportamental": "Comportamental",
    "tecnica": "Técnica (geral)",
    "situacional": "Situacional",
    "lideranca": "Liderança e Gestão",
    "vendas": "Vendas",
    "marketing": "Marketing",
    "atendimento_cliente": "Atendimento ao Cliente",
    "recursos_humanos": "Recursos Humanos",
    "financas": "Finanças e Contabilidade",
    "ti_programacao": "TI / Programação",
    "dados_analytics": "Dados e Analytics",
    "design": "Design e UX",
    "engenharia": "Engenharia",
    "juridico": "Jurídico",
    "saude": "Saúde",
    "educacao": "Educação",
}


class GerarPerguntasService:
    def __init__(self, dados, usuario_id, origem=ORIGEM_BANCO):
        self.dados = dados or {}
        self.usuario_id = usuario_id
        # Definida por quem chama (nunca pelo corpo da requisição): as perguntas
        # de uma simulação são criadas com origem "simulacao" e ficam fora da
        # tela Perguntas.
        self.origem = origem

    def execute(self):
        quantidade = max(1, min(int(self.dados.get("quantidade", 5)), 10))
        categoria = self.dados.get("categoria", "comportamental")
        dificuldade = self.dados.get("dificuldade", "media")
        rotulo_categoria = CATEGORIAS.get(categoria, categoria)

        prompt = f"""Você é um especialista em recrutamento e entrevistas de emprego.
Gere exatamente {quantidade} perguntas de entrevista para o JobReady.
Área/categoria: {rotulo_categoria}.
Dificuldade: {dificuldade}.

As perguntas devem ser realistas, diferentes entre si, específicas para a área indicada
e adequadas para candidatos a vagas de emprego nessa área.
Para cada pergunta, gere também uma sugestão curta de resposta que ajude o candidato a estudar.

Responda SOMENTE com um JSON válido, sem markdown, sem comentários e sem texto adicional, neste formato:
[{{"texto": "...", "sugestao_resposta": "..."}}]"""

        response = gerar_conteudo(prompt, temperature=0.8, max_output_tokens=3000)

        try:
            perguntas = extrair_json(response.text)
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError("O Gemini retornou uma resposta inválida. Tente novamente.") from exc

        if not isinstance(perguntas, list):
            raise RuntimeError("O Gemini não retornou uma lista de perguntas válida.")

        # Mesmo que o Gemini devolva mais itens do que o pedido (ou itens com
        # um campo "categoria" próprio), aqui limitamos à quantidade
        # solicitada e SEMPRE gravamos com a categoria/dificuldade escolhidas
        # pelo usuário no formulário — o valor que o modelo eventualmente
        # tenha colocado dentro do JSON é ignorado de propósito.
        criadas = []
        for item in perguntas[:quantidade]:
            if not isinstance(item, dict) or not item.get("texto"):
                continue
            criadas.append(
                Pergunta.criar(
                    usuario_id=self.usuario_id,
                    origem=self.origem,
                    texto=str(item["texto"]).strip(),
                    categoria=categoria,
                    dificuldade=dificuldade,
                    sugestao_resposta=str(item.get("sugestao_resposta") or "").strip(),
                )
            )

        if not criadas:
            raise RuntimeError("Não foi possível criar perguntas com o retorno do Gemini.")

        return criadas
