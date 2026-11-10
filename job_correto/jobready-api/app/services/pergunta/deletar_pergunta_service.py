from app.services.pergunta.buscar_pergunta_service import BuscarPerguntaService


class DeletarPerguntaService:

    def __init__(self, pergunta_id, usuario_id):
        self.pergunta_id = pergunta_id
        self.usuario_id = usuario_id

    def execute(self):
        pergunta = BuscarPerguntaService(self.pergunta_id, self.usuario_id).execute()
        pergunta.deletar()
