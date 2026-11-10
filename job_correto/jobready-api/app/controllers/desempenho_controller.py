from flask import Blueprint, jsonify

from app.services.auth.contexto import usuario_atual
from app.services.desempenho.obter_desempenho_service import ObterDesempenhoService

desempenho_bp = Blueprint("desempenho_bp", __name__)


@desempenho_bp.get("/api/desempenho")
def obter_desempenho():
    return jsonify(ObterDesempenhoService(usuario_atual().id).execute())
