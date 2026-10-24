from datetime import datetime

from app.extensions import db


class Curriculo(db.Model):
    """Model da entidade Currículo (dados e anexo enviado pelo usuário)."""

    __tablename__ = "curriculos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    arquivo_path = db.Column(db.String(500), nullable=True)
    arquivo_mimetype = db.Column(db.String(120), nullable=True)
    conteudo_texto = db.Column(db.Text, nullable=True)
    pontos_fortes = db.Column(db.Text, nullable=True)
    pontos_a_melhorar = db.Column(db.Text, nullable=True)
    nota_ia = db.Column(db.Float, nullable=True)          # nota de 0 a 10 dada pela IA
    avaliado_em = db.Column(db.DateTime, nullable=True)
    enviado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def criar(cls, usuario_id, nome_arquivo, conteudo_texto=None,
              pontos_fortes=None, pontos_a_melhorar=None,
              arquivo_path=None, arquivo_mimetype=None):
        curriculo = cls(
            usuario_id=usuario_id,
            nome_arquivo=nome_arquivo,
            arquivo_path=arquivo_path,
            arquivo_mimetype=arquivo_mimetype,
            conteudo_texto=conteudo_texto,
            pontos_fortes=pontos_fortes,
            pontos_a_melhorar=pontos_a_melhorar,
        )
        db.session.add(curriculo)
        db.session.commit()
        return curriculo

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.id).all()

    @classmethod
    def buscar_por_id(cls, curriculo_id):
        return db.session.get(cls, curriculo_id)

    def atualizar(self, nome_arquivo=None, conteudo_texto=None,
                  pontos_fortes=None, pontos_a_melhorar=None,
                  arquivo_path=None, arquivo_mimetype=None):
        if nome_arquivo is not None:
            self.nome_arquivo = nome_arquivo
        if conteudo_texto is not None:
            self.conteudo_texto = conteudo_texto
        if pontos_fortes is not None:
            self.pontos_fortes = pontos_fortes
        if pontos_a_melhorar is not None:
            self.pontos_a_melhorar = pontos_a_melhorar
        if arquivo_path is not None:
            self.arquivo_path = arquivo_path
        if arquivo_mimetype is not None:
            self.arquivo_mimetype = arquivo_mimetype
        db.session.commit()
        return self

    def definir_avaliacao_ia(self, nota, pontos_fortes, pontos_a_melhorar):
        self.nota_ia = nota
        self.pontos_fortes = pontos_fortes
        self.pontos_a_melhorar = pontos_a_melhorar
        self.avaliado_em = datetime.utcnow()
        db.session.commit()
        return self

    def invalidar_nota(self):
        """A nota deixa de valer quando o conteúdo do currículo muda."""
        self.nota_ia = None
        self.avaliado_em = None
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "nome_arquivo": self.nome_arquivo,
            "arquivo_mimetype": self.arquivo_mimetype,
            "arquivo_url": f"/api/curriculos/{self.id}/arquivo" if self.arquivo_path else None,
            "tem_anexo": bool(self.arquivo_path),
            "conteudo_texto": self.conteudo_texto,
            "pontos_fortes": self.pontos_fortes,
            "pontos_a_melhorar": self.pontos_a_melhorar,
            "nota_ia": self.nota_ia,
            "avaliado_em": self.avaliado_em.isoformat() if self.avaliado_em else None,
            "enviado_em": self.enviado_em.isoformat() if self.enviado_em else None,
        }
