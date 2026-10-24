from datetime import datetime

from werkzeug.security import generate_password_hash

from app.extensions import db


class Usuario(db.Model):
    """Model da entidade Usuário (cadastro e login)."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    curriculos = db.relationship("Curriculo", backref="usuario", cascade="all, delete-orphan")
    entrevistas = db.relationship("Entrevista", backref="usuario", cascade="all, delete-orphan")
    lembretes = db.relationship("Lembrete", backref="usuario", cascade="all, delete-orphan")

    @classmethod
    def criar(cls, nome, email, senha):
        usuario = cls(nome=nome.strip(), email=email.strip().lower())
        usuario.definir_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        return usuario

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def buscar_por_id(cls, usuario_id):
        return db.session.get(cls, usuario_id)

    @classmethod
    def buscar_por_email(cls, email):
        if not email:
            return None
        return cls.query.filter_by(email=email.strip().lower()).first()

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def atualizar(self, nome=None, email=None, senha=None):
        if nome is not None and nome.strip():
            self.nome = nome.strip()
        if email is not None and email.strip():
            self.email = email.strip().lower()
        if senha:
            self.definir_senha(senha)
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
