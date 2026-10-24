from app.models.entrevista import Entrevista

TIPO_SIMULACAO = "simulacao_cronometrada"
TOLERANCIA_SEG = 5  # folga (rede/latência) antes de marcar a resposta como "fora do tempo"


def buscar_simulacao(entrevista_id, usuario_id):
    """Busca a simulação garantindo que existe, é do usuário e é do tipo certo."""
    entrevista = Entrevista.buscar_por_id(entrevista_id)
    if not entrevista or entrevista.tipo != TIPO_SIMULACAO:
        raise LookupError("Simulação não encontrada.")
    if entrevista.usuario_id != usuario_id:
        raise PermissionError("Você não tem permissão para acessar esta simulação.")
    return entrevista


def serializar(entrevista, feedback=None):
    """Estado completo da simulação (usado ao iniciar, retomar e exibir o resultado)."""
    from datetime import datetime

    itens = list(entrevista.simulacao_itens)
    atual = next((i for i in itens if not i.respondida), None)
    dados = {
        **entrevista.to_dict(),
        "cronometrada": all(i.cronometrada for i in itens) if itens else False,
        "total": len(itens),
        "respondidas": sum(1 for i in itens if i.respondida),
        "itens": [i.to_dict() for i in itens],
        "item_atual": None,
        "feedback": None,
    }
    if atual and entrevista.status == "em_andamento":
        dados["item_atual"] = {
            **atual.to_dict(incluir_resposta=False),
            "restante_seg": atual.restante_seg(datetime.utcnow()),
        }
    if feedback is None and entrevista.feedbacks:
        feedback = entrevista.feedbacks[-1]
    if feedback is not None:
        dados["feedback"] = feedback.to_dict()
    return dados
