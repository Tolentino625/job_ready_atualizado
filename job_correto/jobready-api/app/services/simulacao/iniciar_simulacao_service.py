from datetime import datetime

from app.extensions import db
from app.models.entrevista import Entrevista
from app.models.simulacao_item import SimulacaoItem
from app.models.pergunta import ORIGEM_SIMULACAO
from app.services.pergunta.gerar_perguntas_service import CATEGORIAS, GerarPerguntasService
from app.services.simulacao.comum import TIPO_SIMULACAO, serializar

DIFICULDADES = ("facil", "media", "dificil")
QUANTIDADE_MIN, QUANTIDADE_MAX = 3, 10
TEMPO_MIN, TEMPO_MAX = 30, 600


class IniciarSimulacaoService:
    """Caso de uso: iniciar uma simulação (cronometrada ou sem limite de tempo).

    Gera a sequência de perguntas com o Gemini (reaproveitando o gerador de
    perguntas existente), cria a Entrevista do tipo simulação e um item por
    pergunta, e dispara o cronômetro da primeira.
    """

    def __init__(self, dados, usuario_id):
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def _validar(self):
        try:
            quantidade = int(self.dados.get("quantidade", 5))
            tempo = int(self.dados.get("tempo_por_pergunta", 120))
        except (TypeError, ValueError):
            raise ValueError("'quantidade' e 'tempo_por_pergunta' devem ser números inteiros.")
        categoria = self.dados.get("categoria", "comportamental")
        dificuldade = self.dados.get("dificuldade", "media")

        if not QUANTIDADE_MIN <= quantidade <= QUANTIDADE_MAX:
            raise ValueError(f"A quantidade de perguntas deve ficar entre {QUANTIDADE_MIN} e {QUANTIDADE_MAX}.")
        # tempo 0 = simulação sem cronômetro
        if tempo != 0 and not TEMPO_MIN <= tempo <= TEMPO_MAX:
            raise ValueError(
                f"O tempo por pergunta deve ser 0 (sem limite) ou ficar entre {TEMPO_MIN} e {TEMPO_MAX} segundos."
            )
        if categoria not in CATEGORIAS:
            raise ValueError("Categoria inválida.")
        if dificuldade not in DIFICULDADES:
            raise ValueError("Dificuldade inválida.")
        return quantidade, tempo, categoria, dificuldade

    def execute(self):
        quantidade, tempo, categoria, dificuldade = self._validar()

        # Gera primeiro: se o Gemini falhar, nenhuma entrevista fica pendurada.
        perguntas = GerarPerguntasService(
            {"quantidade": quantidade, "categoria": categoria, "dificuldade": dificuldade},
            self.usuario_id,
            origem=ORIGEM_SIMULACAO,   # fica só na simulação, fora da tela Perguntas
        ).execute()

        agora = datetime.utcnow()
        entrevista = Entrevista(usuario_id=self.usuario_id, tipo=TIPO_SIMULACAO, status="em_andamento")
        db.session.add(entrevista)
        db.session.flush()
        for ordem, pergunta in enumerate(perguntas, start=1):
            db.session.add(SimulacaoItem(
                entrevista_id=entrevista.id,
                pergunta_id=pergunta.id,
                ordem=ordem,
                tempo_limite_seg=tempo,
                liberada_em=agora if ordem == 1 else None,
            ))
        db.session.commit()
        return serializar(entrevista)
