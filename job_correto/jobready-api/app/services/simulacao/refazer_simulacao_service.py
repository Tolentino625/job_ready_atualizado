from datetime import datetime

from app.extensions import db
from app.models.entrevista import Entrevista
from app.models.simulacao_item import SimulacaoItem
from app.services.simulacao.comum import TIPO_SIMULACAO, buscar_simulacao, serializar


class RefazerSimulacaoService:

    def __init__(self, entrevista_id, usuario_id):
        self.entrevista_id = entrevista_id
        self.usuario_id = usuario_id

    def execute(self):
        original = buscar_simulacao(self.entrevista_id, self.usuario_id)
        if original.status != "concluida":
            raise ValueError("Só é possível tentar novamente uma simulação já concluída.")

        base = [i for i in original.simulacao_itens if i.pergunta is not None]
        if not base:
            raise ValueError("As perguntas desta simulação não existem mais.")

        agora = datetime.utcnow()
        nova = Entrevista(usuario_id=self.usuario_id, tipo=TIPO_SIMULACAO, status="em_andamento")
        db.session.add(nova)
        db.session.flush()
        for ordem, item in enumerate(base, start=1):
            db.session.add(SimulacaoItem(
                entrevista_id=nova.id,
                pergunta_id=item.pergunta_id,
                ordem=ordem,
                tempo_limite_seg=item.tempo_limite_seg,
                liberada_em=agora if ordem == 1 else None,
            ))
        db.session.commit()
        return serializar(nova)
