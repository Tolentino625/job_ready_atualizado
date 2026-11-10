from app.models.lembrete import Lembrete


class ListarLembretesService:

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        return Lembrete.listar_por_usuario(self.usuario_id)
