from app.services.pergunta.buscar_pergunta_service import BuscarPerguntaService
from app.models.resposta import Resposta
from app.services.entrevista.obter_entrevista_pratica_service import ObterEntrevistaPraticaService


class ResponderPerguntaService:

    def __init__(self, pergunta_id, dados, usuario_id):
        self.pergunta_id = pergunta_id
        self.dados = dados or {}
        self.usuario_id = usuario_id

    def execute(self):
        texto_resposta = (self.dados.get("texto_resposta") or "").strip()
        if not texto_resposta:
            raise ValueError("O campo 'texto_resposta' é obrigatório.")

        BuscarPerguntaService(self.pergunta_id, self.usuario_id).execute()

        entrevista = ObterEntrevistaPraticaService(self.usuario_id).execute()

        resposta_existente = Resposta.query.filter_by(
            entrevista_id=entrevista.id, pergunta_id=self.pergunta_id
        ).first()

        if resposta_existente:
            return resposta_existente.atualizar(texto_resposta=texto_resposta)

        return Resposta.criar(
            entrevista_id=entrevista.id,
            pergunta_id=self.pergunta_id,
            texto_resposta=texto_resposta,
        )
