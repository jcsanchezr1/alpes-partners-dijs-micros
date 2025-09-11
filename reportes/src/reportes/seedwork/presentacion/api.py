from flask import Blueprint, request, jsonify
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def crear_blueprint_base(nombre: str, prefijo_url: str = None) -> Blueprint:
    """Crea un blueprint base con configuraciones comunes."""
    blueprint = Blueprint(
        nombre, 
        __name__, 
        url_prefix=prefijo_url or f'/{nombre}'
    )
    
    @blueprint.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @blueprint.errorhandler(500)
    def internal_error(error):
        logger.error(f"Error interno: {error}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return blueprint
