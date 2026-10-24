from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
from flask.views import MethodView

from app.services.auth.contexto import usuario_atual
from app.services.curriculo.criar_curriculo_service import CriarCurriculoService
from app.services.curriculo.listar_curriculos_service import ListarCurriculosService
from app.services.curriculo.buscar_curriculo_service import BuscarCurriculoService
from app.services.curriculo.atualizar_curriculo_service import AtualizarCurriculoService
from app.services.curriculo.deletar_curriculo_service import DeletarCurriculoService
from app.services.curriculo.avaliar_curriculo_service import AvaliarCurriculoService
from app.services.ia.gemini_client import GeminiIndisponivelError, GeminiCotaExcedidaError

curriculo_bp = Blueprint("curriculo_bp", __name__)


class CurriculoListController(MethodView):
    def get(self):
        curriculos = ListarCurriculosService(usuario_atual().id).execute()
        return jsonify([c.to_dict() for c in curriculos])

    def post(self):
        try:
            # Importante: checar pelo Content-Type, não por request.files. Um
            # FormData enviado pelo navegador é multipart mesmo quando nenhum
            # arquivo foi selecionado, e nesse caso request.files vem vazio
            # (o que antes fazia cair, por engano, no branch de JSON e
            # quebrar com um 400 bruto do Werkzeug).
            if request.mimetype == "multipart/form-data":
                dados = request.form.to_dict()
                arquivo = request.files.get("arquivo")
            else:
                dados = request.get_json(force=True) or {}
                arquivo = None
            curriculo = CriarCurriculoService(dados, arquivo, usuario_atual().id).execute()
            return jsonify(curriculo.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400


class CurriculoDetailController(MethodView):
    def get(self, curriculo_id):
        try:
            curriculo = BuscarCurriculoService(curriculo_id, usuario_atual().id).execute()
            return jsonify(curriculo.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403

    def put(self, curriculo_id):
        try:
            if request.mimetype == "multipart/form-data":
                dados = request.form.to_dict()
                arquivo = request.files.get("arquivo")
            else:
                dados = request.get_json(force=True) or {}
                arquivo = None
            curriculo = AtualizarCurriculoService(curriculo_id, dados, arquivo, usuario_atual().id).execute()
            return jsonify(curriculo.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    def delete(self, curriculo_id):
        try:
            DeletarCurriculoService(curriculo_id, usuario_atual().id).execute()
            return jsonify({"mensagem": "Currículo excluído com sucesso."})
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403


@curriculo_bp.post("/api/curriculos/<int:curriculo_id>/avaliar")
def avaliar_curriculo(curriculo_id):
    """Pede ao Gemini uma avaliação do currículo (pontos fortes / a
    melhorar) e devolve o currículo já atualizado com o feedback."""
    try:
        curriculo = AvaliarCurriculoService(curriculo_id, usuario_atual().id).execute()
        return jsonify(curriculo.to_dict())
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except GeminiCotaExcedidaError as e:
        return jsonify({"erro": str(e)}), 429
    except GeminiIndisponivelError as e:
        return jsonify({"erro": str(e)}), 503
    except RuntimeError as e:
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        # Mesmo tratamento usado na geração de perguntas: garante resposta
        # JSON com CORS em vez de um 500 "cru" (ex: chave inválida, SDK não
        # instalado, falha de rede ao chamar o Gemini).
        return jsonify({"erro": f"Falha ao chamar o Gemini: {e}"}), 500


@curriculo_bp.get("/api/curriculos/<int:curriculo_id>/arquivo")
def baixar_arquivo(curriculo_id):
    try:
        curriculo = BuscarCurriculoService(curriculo_id, usuario_atual().id).execute()
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except PermissionError as e:
        return jsonify({"erro": str(e)}), 403

    if not curriculo.arquivo_path:
        return jsonify({"erro": "Este currículo não possui anexo."}), 404

    base = Path(__file__).resolve().parents[2]
    caminho = (base / curriculo.arquivo_path).resolve()
    try:
        caminho.relative_to(base.resolve())
    except ValueError:
        return jsonify({"erro": "Arquivo inválido."}), 400

    if not caminho.is_file():
        return jsonify({"erro": "O arquivo não foi encontrado no servidor."}), 404

    return send_file(
        caminho,
        mimetype=curriculo.arquivo_mimetype or "application/octet-stream",
        download_name=curriculo.nome_arquivo,
        as_attachment=False,
    )


curriculo_bp.add_url_rule(
    "/api/curriculos", view_func=CurriculoListController.as_view("curriculo_list")
)
curriculo_bp.add_url_rule(
    "/api/curriculos/<int:curriculo_id>", view_func=CurriculoDetailController.as_view("curriculo_detail")
)
