from datetime import datetime
from app.extensions import db
from app.models.entrevista import Entrevista


class Feedback(db.Model):
    """Model da entidade Feedback (feedback de desempenho de uma entrevista)."""

    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    entrevista_id = db.Column(db.Integer, db.ForeignKey("entrevistas.id"), nullable=False)
    pontuacao = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    ponto_forte = db.Column(db.String(255), nullable=True)
    ponto_a_melhorar = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, entrevista_id, pontuacao, comentario=None, ponto_forte=None, ponto_a_melhorar=None):
        feedback = cls(
            entrevista_id=entrevista_id,
            pontuacao=pontuacao,
            comentario=comentario,
            ponto_forte=ponto_forte,
            ponto_a_melhorar=ponto_a_melhorar,
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        return (
            cls.query.join(Entrevista, Feedback.entrevista_id == Entrevista.id)
            .filter(Entrevista.usuario_id == usuario_id)
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def buscar_por_id(cls, feedback_id):
        return cls.query.get(feedback_id)

    def atualizar(self, pontuacao=None, comentario=None, ponto_forte=None, ponto_a_melhorar=None):
        if pontuacao is not None:
            self.pontuacao = pontuacao
        if comentario is not None:
            self.comentario = comentario
        if ponto_forte is not None:
            self.ponto_forte = ponto_forte
        if ponto_a_melhorar is not None:
            self.ponto_a_melhorar = ponto_a_melhorar
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "entrevista_id": self.entrevista_id,
            "pontuacao": self.pontuacao,
            "comentario": self.comentario,
            "ponto_forte": self.ponto_forte,
            "ponto_a_melhorar": self.ponto_a_melhorar,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
