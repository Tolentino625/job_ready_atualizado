import secrets
from functools import wraps

from flask import request
from werkzeug.security import check_password_hash

from app.models.usuario import Usuario

# Para o projeto local, os tokens ficam em memória. Reiniciar a API encerra
# as sessões ativas, o que é adequado para o ambiente de desenvolvimento.
_TOKENS = {}


def autenticar(email, senha):
    if not email or not senha:
        raise ValueError("E-mail e senha são obrigatórios.")

    usuario = Usuario.buscar_por_email(email)
    if not usuario:
        raise ValueError("E-mail ou senha inválidos.")

    senha_valida = False
    try:
        senha_valida = check_password_hash(usuario.senha, senha)
    except (ValueError, TypeError):
        senha_valida = False

    # Compatibilidade com usuários antigos que tenham senha em texto puro.
    if not senha_valida and usuario.senha == senha:
        senha_valida = True
        usuario.definir_senha(senha)

    if not senha_valida:
        raise ValueError("E-mail ou senha inválidos.")

    token = secrets.token_urlsafe(32)
    _TOKENS[token] = usuario.id
    return token, usuario


def obter_usuario_por_token(token):
    usuario_id = _TOKENS.get(token)
    if not usuario_id:
        return None
    return Usuario.buscar_por_id(usuario_id)


def token_da_requisicao():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


def usuario_autenticado():
    token = token_da_requisicao()
    return obter_usuario_por_token(token) if token else None


def requer_autenticacao(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        usuario = usuario_autenticado()
        if not usuario:
            from flask import jsonify
            return jsonify({"erro": "Autenticação necessária."}), 401
        return view(*args, **kwargs)
    return wrapped


def sair(token):
    if token:
        _TOKENS.pop(token, None)
