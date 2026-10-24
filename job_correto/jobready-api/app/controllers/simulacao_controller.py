from flask import Blueprint, jsonify, request

from app.services.auth.contexto import usuario_atual
from app.services.ia.gemini_client import GeminiCotaExcedidaError, GeminiIndisponivelError
from app.services.simulacao.buscar_simulacao_service import BuscarSimulacaoService
from app.services.simulacao.finalizar_simulacao_service import FinalizarSimulacaoService
from app.services.simulacao.iniciar_simulacao_service import IniciarSimulacaoService
from app.services.simulacao.listar_simulacoes_service import ListarSimulacoesService
from app.services.simulacao.refazer_simulacao_service import RefazerSimulacaoService
from app.services.simulacao.responder_simulacao_service import ResponderSimulacaoService

simulacao_bp = Blueprint("simulacao_bp", __name__)


def _erro_ia(e):
    """Mesmo tratamento de erros do Gemini usado nas demais rotas de IA."""
    if isinstance(e, GeminiCotaExcedidaError):
        return jsonify({"erro": str(e)}), 429
    if isinstance(e, GeminiIndisponivelError):
        return jsonify({"erro": str(e)}), 503
    if isinstance(e, RuntimeError):
        return jsonify({"erro": str(e)}), 500
    return jsonify({"erro": f"Falha ao chamar o Gemini: {e}"}), 500


@simulacao_bp.get("/api/simulacoes")
def listar_simulacoes():
    return jsonify(ListarSimulacoesService(usuario_atual().id).execute())


@simulacao_bp.post("/api/simulacoes")
def iniciar_simulacao():
    try:
        dados = IniciarSimulacaoService(request.get_json(force=True) or {}, usuario_atual().id).execute()
        return jsonify(dados), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:  # inclui falhas do Gemini
        return _erro_ia(e)


@simulacao_bp.get("/api/simulacoes/<int:entrevista_id>")
def buscar_simulacao(entrevista_id):
    try:
        return jsonify(BuscarSimulacaoService(entrevista_id, usuario_atual().id).execute())
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403


@simulacao_bp.post("/api/simulacoes/<int:entrevista_id>/responder")
def responder_simulacao(entrevista_id):
    try:
        dados = ResponderSimulacaoService(
            entrevista_id, request.get_json(force=True) or {}, usuario_atual().id
        ).execute()
        return jsonify(dados), 201
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except (ValueError, TypeError) as e:
        return jsonify({"erro": str(e)}), 400


@simulacao_bp.post("/api/simulacoes/<int:entrevista_id>/refazer")
def refazer_simulacao(entrevista_id):
    try:
        return jsonify(RefazerSimulacaoService(entrevista_id, usuario_atual().id).execute()), 201
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@simulacao_bp.post("/api/simulacoes/<int:entrevista_id>/finalizar")
def finalizar_simulacao(entrevista_id):
    try:
        return jsonify(FinalizarSimulacaoService(entrevista_id, usuario_atual().id).execute())
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return _erro_ia(e)
