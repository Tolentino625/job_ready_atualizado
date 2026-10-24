from datetime import datetime

from app.extensions import db
from app.models.resposta import Resposta
from app.services.simulacao.comum import TOLERANCIA_SEG, buscar_simulacao, serializar

SEM_RESPOSTA = "(sem resposta)"
MAX_CARACTERES = 5000


class ResponderSimulacaoService:
    """Caso de uso: registrar a resposta da pergunta atual da simulação.

    O tempo gasto é medido pelo servidor (a partir de `liberada_em`), então não
    depende do que o navegador informa. Respostas vazias (pulada ou tempo
    esgotado sem digitar nada) também geram uma Resposta com ID, nota 0.
    """

    def __init__(self, entrevista_id, dados, usuario_id):
        self.entrevista_id = entrevista_id
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        entrevista = buscar_simulacao(self.entrevista_id, self.usuario_id)
        if entrevista.status != "em_andamento":
            raise ValueError("Esta simulação já foi encerrada.")

        itens = list(entrevista.simulacao_itens)
        atual = next((i for i in itens if not i.respondida), None)
        if atual is None:
            raise ValueError("Todas as perguntas já foram respondidas. Finalize a simulação.")
        if self.dados.get("item_id") is not None and int(self.dados["item_id"]) != atual.id:
            raise ValueError("Esta não é a pergunta atual da simulação.")

        texto = str(self.dados.get("texto_resposta") or "").strip()
        if len(texto) > MAX_CARACTERES:
            raise ValueError(f"A resposta deve ter no máximo {MAX_CARACTERES} caracteres.")

        agora = datetime.utcnow()
        decorrido = int(max(0, (agora - (atual.liberada_em or agora)).total_seconds()))
        esgotado = atual.cronometrada and decorrido > atual.tempo_limite_seg + TOLERANCIA_SEG

        resposta = Resposta(
            entrevista_id=entrevista.id,
            pergunta_id=atual.pergunta_id,
            texto_resposta=texto or SEM_RESPOSTA,
            tipo="texto",
            respondido_em=agora,
        )
        db.session.add(resposta)
        db.session.flush()

        atual.resposta_id = resposta.id
        atual.respondida_em = agora
        if atual.cronometrada:
            atual.tempo_gasto_seg = min(decorrido, atual.tempo_limite_seg)
            atual.tempo_esgotado = esgotado or (not texto and decorrido >= atual.tempo_limite_seg - 1)
        else:
            atual.tempo_gasto_seg = decorrido
            atual.tempo_esgotado = False

        proximo = next((i for i in itens if i.ordem > atual.ordem), None)
        if proximo:
            proximo.liberada_em = agora
        db.session.commit()
        return serializar(entrevista)
