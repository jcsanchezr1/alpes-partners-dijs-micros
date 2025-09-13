"""Configuración mínima de Flask para contexto de base de datos."""

from flask import Flask
from .settings import settings


def crear_app_minima():
    """Crea aplicación Flask mínima solo para el contexto de base de datos."""
    app = Flask(__name__)
    
    # Configuración de base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar Flask-SQLAlchemy
    from ..seedwork.infraestructura.database import db, init_db_flask_tables
    db.init_app(app)
    
    with app.app_context():
        init_db_flask_tables()
    
    return app
