from flask import Blueprint, jsonify, request

from app.services.auth.auth_service import autenticar, usuario_autenticado, sair
from app.services.auth.registrar_service import RegistrarUsuarioService


auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    try:
        dados = request.get_json(force=True) or {}
        token, usuario = autenticar(dados.get("email"), dados.get("senha"))
        return jsonify({"token": token, "usuario": usuario.to_dict()})
    except ValueError as e:
        return jsonify({"erro": str(e)}), 401


@auth_bp.post("/registro")
def registro():
    try:
        dados = request.get_json(force=True) or {}
        usuario = RegistrarUsuarioService(dados).execute()
        token, usuario = autenticar(usuario.email, dados.get("senha"))
        return jsonify({"token": token, "usuario": usuario.to_dict()}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@auth_bp.get("/me")
def me():
    usuario = usuario_autenticado()
    if not usuario:
        return jsonify({"erro": "Autenticação necessária."}), 401
    return jsonify(usuario.to_dict())


@auth_bp.post("/logout")
def logout():
    # O frontend também apaga o token localmente.
    from app.services.auth.auth_service import token_da_requisicao
    sair(token_da_requisicao())
    return jsonify({"mensagem": "Logout realizado com sucesso."})
