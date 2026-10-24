from flask import Blueprint, jsonify, request
from flask.views import MethodView

from app.services.auth.contexto import usuario_atual
from app.services.usuario.criar_usuario_service import CriarUsuarioService
from app.services.usuario.listar_usuarios_service import ListarUsuariosService
from app.services.usuario.buscar_usuario_service import BuscarUsuarioService
from app.services.usuario.atualizar_usuario_service import AtualizarUsuarioService
from app.services.usuario.deletar_usuario_service import DeletarUsuarioService

usuario_bp = Blueprint("usuario_bp", __name__)


class UsuarioListController(MethodView):
    """Controller (classe) responsável pela coleção /api/usuarios."""

    def get(self):
        # Cada usuário só enxerga o próprio cadastro nesta listagem.
        usuarios = ListarUsuariosService(usuario_atual().id).execute()
        return jsonify([u.to_dict() for u in usuarios])

    def post(self):
        try:
            usuario = CriarUsuarioService(request.get_json(force=True)).execute()
            return jsonify(usuario.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400


class UsuarioDetailController(MethodView):
    """Controller (classe) responsável pelo item /api/usuarios/<id>."""

    def get(self, usuario_id):
        try:
            usuario = BuscarUsuarioService(usuario_id, usuario_atual().id).execute()
            return jsonify(usuario.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403

    def put(self, usuario_id):
        try:
            usuario = AtualizarUsuarioService(
                usuario_id, request.get_json(force=True), usuario_atual().id
            ).execute()
            return jsonify(usuario.to_dict())
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    def delete(self, usuario_id):
        try:
            DeletarUsuarioService(usuario_id, usuario_atual().id).execute()
            return jsonify({"mensagem": "Usuário excluído com sucesso."})
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403


usuario_bp.add_url_rule(
    "/api/usuarios", view_func=UsuarioListController.as_view("usuario_list")
)
usuario_bp.add_url_rule(
    "/api/usuarios/<int:usuario_id>", view_func=UsuarioDetailController.as_view("usuario_detail")
)
