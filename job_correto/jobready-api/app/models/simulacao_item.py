from datetime import datetime

from sqlalchemy.orm import backref

from app.extensions import db


class SimulacaoItem(db.Model):
    """Uma pergunta dentro de uma simulação cronometrada.

    A simulação em si é uma `Entrevista` (tipo="simulacao_cronometrada"); esta
    tabela guarda, para cada pergunta da sequência, a ordem, o tempo limite e
    o tempo realmente gasto, e aponta para a `Resposta` (que carrega o ID
    público da resposta, a nota e o comentário da IA).
    """

    __tablename__ = "simulacao_itens"

    id = db.Column(db.Integer, primary_key=True)
    entrevista_id = db.Column(db.Integer, db.ForeignKey("entrevistas.id"), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey("perguntas.id"), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    tempo_limite_seg = db.Column(db.Integer, nullable=False)  # 0 = sem limite de tempo (não cronometrada)
    liberada_em = db.Column(db.DateTime, nullable=True)   # quando o cronômetro desta pergunta começou
    respondida_em = db.Column(db.DateTime, nullable=True)
    tempo_gasto_seg = db.Column(db.Integer, nullable=True)
    tempo_esgotado = db.Column(db.Boolean, nullable=False, default=False)
    resposta_id = db.Column(db.Integer, db.ForeignKey("respostas.id"), nullable=True)

    pergunta = db.relationship("Pergunta")
    resposta = db.relationship("Resposta")
    entrevista = db.relationship(
        "Entrevista",
        backref=backref("simulacao_itens", cascade="all, delete-orphan", order_by="SimulacaoItem.ordem"),
    )

    @property
    def respondida(self):
        return self.respondida_em is not None

    @property
    def cronometrada(self):
        return bool(self.tempo_limite_seg)

    def restante_seg(self, agora=None):
        """Segundos que ainda restam no cronômetro desta pergunta (0 se já estourou;
        None se a simulação não é cronometrada)."""
        if not self.cronometrada:
            return None
        if self.respondida or not self.liberada_em:
            return 0 if self.respondida else self.tempo_limite_seg
        agora = agora or datetime.utcnow()
        decorrido = (agora - self.liberada_em).total_seconds()
        return max(0, int(round(self.tempo_limite_seg - decorrido)))

    def to_dict(self, incluir_resposta=True):
        resposta = self.resposta if incluir_resposta else None
        return {
            "item_id": self.id,
            "ordem": self.ordem,
            "pergunta_id": self.pergunta_id,
            "pergunta": self.pergunta.texto if self.pergunta else None,
            "categoria": self.pergunta.categoria if self.pergunta else None,
            "tempo_limite_seg": self.tempo_limite_seg or None,
            "cronometrada": self.cronometrada,
            "tempo_gasto_seg": self.tempo_gasto_seg,
            "tempo_esgotado": bool(self.tempo_esgotado),
            "respondida": self.respondida,
            "resposta_id": self.resposta_id,
            "texto_resposta": resposta.texto_resposta if resposta else None,
            "nota": resposta.nota_ia if resposta else None,
            "comentario": resposta.comentario_ia if resposta else None,
        }
