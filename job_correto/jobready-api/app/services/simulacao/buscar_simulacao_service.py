from app.services.simulacao.comum import buscar_simulacao, serializar


class BuscarSimulacaoService:

    def __init__(self, entrevista_id, usuario_id):
        self.entrevista_id = entrevista_id
        self.usuario_id = usuario_id

    def execute(self):
        return serializar(buscar_simulacao(self.entrevista_id, self.usuario_id))
