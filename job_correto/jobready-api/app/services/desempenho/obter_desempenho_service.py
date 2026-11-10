from app.repositories.desempenho_repository import DesempenhoRepository


class ObterDesempenhoService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return {
            "estatisticas": DesempenhoRepository.calcular_estatisticas_desempenho_usuario(self.usuario_id),
            "gargalos": DesempenhoRepository.detectar_gargalos_sequenciais(self.usuario_id),
            "criterios": {
                "nota_minima_adequada": DesempenhoRepository.NOTA_MINIMA_ADEQUADA,
                "tamanho_minimo_sequencia": DesempenhoRepository.TAMANHO_MINIMO_SEQUENCIA,
            },
        }
