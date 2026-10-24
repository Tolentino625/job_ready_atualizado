from app.services.lembrete.buscar_lembrete_service import BuscarLembreteService


class DeletarLembreteService:
    def __init__(self, lembrete_id, usuario_id):
        self.lembrete_id = lembrete_id
        self.usuario_id = usuario_id

    def execute(self):
        lembrete = BuscarLembreteService(self.lembrete_id, self.usuario_id).execute()
        lembrete.deletar()
