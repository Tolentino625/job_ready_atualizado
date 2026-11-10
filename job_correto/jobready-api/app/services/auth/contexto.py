from flask import g


def usuario_atual():
    return getattr(g, "usuario_atual", None)
