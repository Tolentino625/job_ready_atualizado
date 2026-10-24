from flask import Blueprint, jsonify, request
from flask.views import MethodView

from app.services.auth.contexto import usuario_atual
from app.services.feedback.criar_feedback_service import CriarFeedbackService
from app.services.feedback.listar_feedbacks_service import ListarFeedbacksService
from app.services.feedback.buscar_feedback_service import BuscarFeedbackService
from app.services.feedback.atualizar_feedback_service import AtualizarFeedbackService
from app.services.feedback.deletar_feedback_service import DeletarFeedbackService

feedback_bp = Blueprint("feedback_bp", __name__)


class FeedbackListController(MethodView):
    """Controller (classe) responsável pela coleção /api/feedbacks."""

    def get(self):
        feedbacks = ListarFeedbacksService(usuario_atual().id).execute()
        return jsonify([f.to_dict() for f in feedbacks])

    def post(self):
        try:
            feedback = CriarFeedbackService(request.get_json(force=True), usuario_atual().id).execute()
            return jsonify(feedback.to_dict()), 201
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400


class FeedbackDetailController(MethodView):
    """Controller (classe) responsável pelo item /api/feedbacks/<id>."""

    def get(self, feedback_id):
        try:
            feedback = BuscarFeedbackService(feedback_id, usuario_atual().id).execute()
            return jsonify(feedback.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403

    def put(self, feedback_id):
        try:
            feedback = AtualizarFeedbackService(
                feedback_id, request.get_json(force=True), usuario_atual().id
            ).execute()
            return jsonify(feedback.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    def delete(self, feedback_id):
        try:
            DeletarFeedbackService(feedback_id, usuario_atual().id).execute()
            return jsonify({"mensagem": "Feedback excluído com sucesso."})
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403


feedback_bp.add_url_rule(
    "/api/feedbacks", view_func=FeedbackListController.as_view("feedback_list")
)
feedback_bp.add_url_rule(
    "/api/feedbacks/<int:feedback_id>", view_func=FeedbackDetailController.as_view("feedback_detail")
)
