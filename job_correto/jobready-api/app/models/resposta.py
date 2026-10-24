from datetime import datetime
from app.extensions import db
from app.models.entrevista import Entrevista


class Resposta(db.Model):
    """Model da entidade Resposta (resposta do usuário a uma pergunta, por voz ou texto)."""

    __tablename__ = "respostas"

    id = db.Column(db.Integer, primary_key=True)
    entrevista_id = db.Column(db.Integer, db.ForeignKey("entrevistas.id"), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey("perguntas.id"), nullable=False)
    texto_resposta = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="texto")  # 'voz' ou 'texto'
    respondido_em = db.Column(db.DateTime, default=datetime.utcnow)
    nota_ia = db.Column(db.Float, nullable=True)
    comentario_ia = db.Column(db.Text, nullable=True)
    avaliado_em = db.Column(db.DateTime, nullable=True)

    pergunta = db.relationship("Pergunta")

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, entrevista_id, pergunta_id, texto_resposta, tipo="texto"):
        resposta = cls(
            entrevista_id=entrevista_id,
            pergunta_id=pergunta_id,
            texto_resposta=texto_resposta,
            tipo=tipo,
        )
        db.session.add(resposta)
        db.session.commit()
        return resposta

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        return (
            cls.query.join(Entrevista, Resposta.entrevista_id == Entrevista.id)
            .filter(Entrevista.usuario_id == usuario_id)
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def buscar_por_id(cls, resposta_id):
        return cls.query.get(resposta_id)

    def atualizar(self, texto_resposta=None, tipo=None):
        if texto_resposta is not None:
            self.texto_resposta = texto_resposta
            # Se o texto da resposta muda, a nota anterior perde validade.
            self.nota_ia = None
            self.comentario_ia = None
            self.avaliado_em = None
        if tipo is not None:
            self.tipo = tipo
        db.session.commit()
        return self

    def definir_avaliacao_ia(self, nota, comentario):
        self.nota_ia = nota
        self.comentario_ia = comentario
        self.avaliado_em = datetime.utcnow()
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "entrevista_id": self.entrevista_id,
            "pergunta_id": self.pergunta_id,
            "texto_resposta": self.texto_resposta,
            "tipo": self.tipo,
            "respondido_em": self.respondido_em.isoformat() if self.respondido_em else None,
            "nota_ia": self.nota_ia,
            "comentario_ia": self.comentario_ia,
            "avaliado_em": self.avaliado_em.isoformat() if self.avaliado_em else None,
        }
