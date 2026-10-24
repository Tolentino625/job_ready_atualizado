from datetime import datetime

from app.extensions import db
from app.models.entrevista import Entrevista
from app.models.simulacao_item import SimulacaoItem
from app.services.simulacao.comum import TIPO_SIMULACAO, buscar_simulacao, serializar


class RefazerSimulacaoService:
    """Caso de uso: tentar novamente uma simulação já concluída.

    Cria uma NOVA simulação com as mesmas perguntas, na mesma ordem e com o
    mesmo tempo por pergunta (ou sem limite, se a original era sem cronômetro).
    Não chama o Gemini para gerar perguntas, e a simulação original fica
    intacta, então dá para comparar as notas das tentativas.
    """

    def __init__(self, entrevista_id, usuario_id):
        self.entrevista_id = entrevista_id
        self.usuario_id = usuario_id

    def execute(self):
        original = buscar_simulacao(self.entrevista_id, self.usuario_id)
        if original.status != "concluida":
            raise ValueError("Só é possível tentar novamente uma simulação já concluída.")

        # Ignora perguntas que o usuário tenha excluído do banco desde então.
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
