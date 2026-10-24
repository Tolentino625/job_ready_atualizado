"""
Instâncias das extensões usadas pela aplicação.
Ficam num módulo separado para evitar import circular entre
app/__init__.py e os Models.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
