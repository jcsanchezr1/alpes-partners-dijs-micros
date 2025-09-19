"""Configuración mínima de Flask para el BFF."""

from flask import Flask
from .settings import settings


def crear_app_minima():
    """Crea aplicación Flask mínima para el BFF."""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['DEBUG'] = settings.debug
    
    return app
