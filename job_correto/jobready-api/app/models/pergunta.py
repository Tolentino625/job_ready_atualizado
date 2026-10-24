from app.extensions import db

ORIGEM_BANCO = "banco"
ORIGEM_SIMULACAO = "simulacao"


class Pergunta(db.Model):
    """Model da entidade Pergunta (banco de perguntas frequentes de entrevista)."""

    __tablename__ = "perguntas"

    id = db.Column(db.Integer, primary_key=True)
    # Dono da pergunta (quem a gerou). Perguntas antigas, criadas antes desta
    # coluna existir, ficam com NULL e não aparecem para nenhum usuário.
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(80), nullable=False, default="comportamental")
    dificuldade = db.Column(db.String(20), nullable=False, default="media")
    sugestao_resposta = db.Column(db.Text, nullable=True)
    # De onde a pergunta veio: "banco" = gerada na tela Perguntas (aparece lá);
    # "simulacao" = gerada para uma simulação de entrevista (fica só na
    # simulação e NÃO aparece na tela Perguntas).
    origem = db.Column(db.String(20), nullable=False, default=ORIGEM_BANCO)

    # ---------- CRUD ----------
    @classmethod
    def criar(cls, texto, categoria="comportamental", dificuldade="media",
              sugestao_resposta=None, usuario_id=None, origem=ORIGEM_BANCO):
        pergunta = cls(
            origem=origem,
            usuario_id=usuario_id,
            texto=texto,
            categoria=categoria,
            dificuldade=dificuldade,
            sugestao_resposta=sugestao_resposta,
        )
        db.session.add(pergunta)
        db.session.commit()
        return pergunta

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        """Perguntas do banco de perguntas do usuário (as geradas para
        simulações de entrevista não entram aqui)."""
        return (
            cls.query.filter_by(usuario_id=usuario_id, origem=ORIGEM_BANCO)
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def buscar_por_id(cls, pergunta_id):
        return cls.query.get(pergunta_id)

    def atualizar(self, texto=None, categoria=None, dificuldade=None, sugestao_resposta=None):
        if texto is not None:
            self.texto = texto
        if categoria is not None:
            self.categoria = categoria
        if dificuldade is not None:
            self.dificuldade = dificuldade
        if sugestao_resposta is not None:
            self.sugestao_resposta = sugestao_resposta
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "texto": self.texto,
            "categoria": self.categoria,
            "dificuldade": self.dificuldade,
            "sugestao_resposta": self.sugestao_resposta,
            "origem": self.origem,
        }
