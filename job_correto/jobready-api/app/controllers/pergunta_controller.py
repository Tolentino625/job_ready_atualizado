from flask import Blueprint, jsonify, request
from flask.views import MethodView

from app.services.auth.contexto import usuario_atual
from app.services.pergunta.listar_perguntas_service import ListarPerguntasService
from app.services.pergunta.buscar_pergunta_service import BuscarPerguntaService
from app.services.pergunta.deletar_pergunta_service import DeletarPerguntaService
from app.services.pergunta.gerar_perguntas_service import GerarPerguntasService
from app.services.pergunta.responder_pergunta_service import ResponderPerguntaService
from app.services.resposta.obter_respostas_usuario_service import ObterRespostasUsuarioService
from app.services.ia.gemini_client import GeminiIndisponivelError, GeminiCotaExcedidaError

pergunta_bp = Blueprint("pergunta_bp", __name__)


class PerguntaListController(MethodView):
    """Controller (classe) responsável pela coleção /api/perguntas.

    Cada usuário só vê as perguntas que ele mesmo gerou (veja
    /api/perguntas/gerar): não há criação ou edição manual nesta tela."""

    def get(self):
        perguntas = ListarPerguntasService(usuario_atual().id).execute()
        respostas_por_pergunta = ObterRespostasUsuarioService(usuario_atual().id).execute()
        resultado = []
        for pergunta in perguntas:
            dados = pergunta.to_dict()
            resposta = respostas_por_pergunta.get(pergunta.id)
            dados["minha_resposta"] = resposta.to_dict() if resposta else None
            resultado.append(dados)
        return jsonify(resultado)


@pergunta_bp.post("/api/perguntas/gerar")
def gerar_perguntas():
    try:
        perguntas = GerarPerguntasService(request.get_json(force=True) or {}, usuario_atual().id).execute()
        return jsonify({"perguntas": [p.to_dict() for p in perguntas]}), 201
    except (ValueError, TypeError) as e:
        return jsonify({"erro": str(e)}), 400
    except GeminiCotaExcedidaError as e:
        return jsonify({"erro": str(e)}), 429
    except GeminiIndisponivelError as e:
        return jsonify({"erro": str(e)}), 503
    except RuntimeError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        # Captura qualquer outro erro (ex: chave do Gemini inválida, falha de
        # rede, pacote não instalado) para sempre devolver JSON com os
        # cabeçalhos de CORS, em vez de deixar o Flask retornar um erro 500
        # "cru" que o navegador reporta como bloqueio de CORS.
        return jsonify({"erro": f"Falha ao chamar o Gemini: {e}"}), 500


@pergunta_bp.post("/api/perguntas/<int:pergunta_id>/responder")
def responder_pergunta(pergunta_id):
    """Usuário autenticado responde (ou reescreve a resposta a) uma pergunta
    do banco. Retorna a resposta salva (sem nota, até ser avaliada)."""
    try:
        resposta = ResponderPerguntaService(
            pergunta_id, request.get_json(force=True) or {}, usuario_atual().id
        ).execute()
        return jsonify(resposta.to_dict()), 201
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


class PerguntaDetailController(MethodView):
    """Controller (classe) responsável pelo item /api/perguntas/<id>."""

    def get(self, pergunta_id):
        try:
            pergunta = BuscarPerguntaService(pergunta_id, usuario_atual().id).execute()
            return jsonify(pergunta.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403

    def delete(self, pergunta_id):
        try:
            DeletarPerguntaService(pergunta_id, usuario_atual().id).execute()
            return jsonify({"mensagem": "Pergunta excluída com sucesso."})
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403


pergunta_bp.add_url_rule(
    "/api/perguntas", view_func=PerguntaListController.as_view("pergunta_list")
)
pergunta_bp.add_url_rule(
    "/api/perguntas/<int:pergunta_id>", view_func=PerguntaDetailController.as_view("pergunta_detail")
)
