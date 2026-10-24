from flask import Blueprint, jsonify, request
from flask.views import MethodView

from app.services.auth.contexto import usuario_atual
from app.services.lembrete.criar_lembrete_service import CriarLembreteService
from app.services.lembrete.listar_lembretes_service import ListarLembretesService
from app.services.lembrete.buscar_lembrete_service import BuscarLembreteService
from app.services.lembrete.atualizar_lembrete_service import AtualizarLembreteService
from app.services.lembrete.deletar_lembrete_service import DeletarLembreteService

lembrete_bp = Blueprint("lembrete_bp", __name__)


class LembreteListController(MethodView):
    def get(self):
        lembretes = ListarLembretesService(usuario_atual().id).execute()
        return jsonify([l.to_dict() for l in lembretes])

    def post(self):
        try:
            lembrete = CriarLembreteService(request.get_json(force=True), usuario_atual().id).execute()
            return jsonify(lembrete.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400


class LembreteDetailController(MethodView):
    def get(self, lembrete_id):
        try:
            return jsonify(BuscarLembreteService(lembrete_id, usuario_atual().id).execute().to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403

    def put(self, lembrete_id):
        try:
            lembrete = AtualizarLembreteService(
                lembrete_id, request.get_json(force=True), usuario_atual().id
            ).execute()
            return jsonify(lembrete.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    def delete(self, lembrete_id):
        try:
            DeletarLembreteService(lembrete_id, usuario_atual().id).execute()
            return jsonify({"mensagem": "Lembrete excluído com sucesso."})
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403


lembrete_bp.add_url_rule(
    "/api/lembretes", view_func=LembreteListController.as_view("lembrete_list")
)
lembrete_bp.add_url_rule(
    "/api/lembretes/<int:lembrete_id>",
    view_func=LembreteDetailController.as_view("lembrete_detail"),
)
