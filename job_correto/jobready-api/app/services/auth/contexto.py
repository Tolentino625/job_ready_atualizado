from flask import g


def usuario_atual():
    """Retorna o usuário autenticado da requisição atual (definido em app/__init__.py)."""
    return getattr(g, "usuario_atual", None)
