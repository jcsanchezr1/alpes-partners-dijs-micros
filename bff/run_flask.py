#!/usr/bin/env python3
"""
Script para ejecutar el microservicio BFF.
Incluye health check y endpoint para iniciar el flujo de saga.
"""

import sys
import os
import logging
from flask import Flask

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from alpes_partners.config.settings import settings
from alpes_partners.config.app import crear_app_minima
from alpes_partners.api.bff import crear_rutas

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal del microservicio BFF."""
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("Microservicio: BFF con endpoints /health y /iniciar-saga")
    
    # Crear aplicación Flask
    app = crear_app_minima()
    
    # Registrar rutas
    crear_rutas(app)
    
    # Obtener puerto de Cloud Run
    port = int(os.environ.get('PORT', 8080))
    
    try:
        # Iniciar servidor HTTP
        logger.info(f"Servidor HTTP iniciado en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=settings.debug)
        
    except KeyboardInterrupt:
        logger.info("Microservicio BFF detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el microservicio BFF: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
