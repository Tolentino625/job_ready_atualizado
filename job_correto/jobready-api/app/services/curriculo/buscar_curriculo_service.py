from app.models.curriculo import Curriculo


class BuscarCurriculoService:
    """Caso de uso: buscar um currículo pelo id, garantindo que pertence ao usuário."""

    def __init__(self, curriculo_id, usuario_id=None):
        self.curriculo_id = curriculo_id
        self.usuario_id = usuario_id

    def execute(self):
        curriculo = Curriculo.buscar_por_id(self.curriculo_id)
        if not curriculo:
            raise LookupError("Currículo não encontrado.")
        if self.usuario_id is not None and curriculo.usuario_id != self.usuario_id:
            raise PermissionError("Você não tem permissão para acessar este currículo.")
        return curriculo
