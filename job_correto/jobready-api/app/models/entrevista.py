from datetime import datetime
from app.extensions import db


class Entrevista(db.Model):
    """Model da entidade Entrevista (simulações de entrevista e histórico)."""

    __tablename__ = "entrevistas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="texto")  # 'voz' ou 'texto'
    status = db.Column(db.String(20), nullable=False, default="em_andamento")
    data_realizacao = db.Column(db.DateTime, default=datetime.utcnow)
    pontuacao_geral = db.Column(db.Float, nullable=True)

    respostas = db.relationship("Resposta", backref="entrevista", cascade="all, delete-orphan")
    feedbacks = db.relationship("Feedback", backref="entrevista", cascade="all, delete-orphan")

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, usuario_id, tipo="texto", status="em_andamento", pontuacao_geral=None):
        entrevista = cls(
            usuario_id=usuario_id,
            tipo=tipo,
            status=status,
            pontuacao_geral=pontuacao_geral,
        )
        db.session.add(entrevista)
        db.session.commit()
        return entrevista

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.id).all()

    @classmethod
    def buscar_por_id(cls, entrevista_id):
        return cls.query.get(entrevista_id)

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "status": self.status,
            "data_realizacao": self.data_realizacao.isoformat() if self.data_realizacao else None,
            "pontuacao_geral": self.pontuacao_geral,
        }
