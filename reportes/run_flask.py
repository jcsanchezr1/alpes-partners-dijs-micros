#!/usr/bin/env python3
"""
Script para ejecutar el microservicio de reportes.
NOTA: Reportes es completamente asíncrono, solo consume eventos.
Este script mantiene compatibilidad con docker-compose pero ejecuta el consumidor.
"""

import sys
import os

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

import logging
from reportes.config.settings import settings
from reportes.modulos.reportes.infraestructura.consumidores import suscribirse_a_eventos_contratos_desde_reportes

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal del microservicio de reportes (solo consumidor)."""
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info("NOTA: Reportes es completamente asíncrono - solo consume eventos")
    
    try:
        # Iniciar el consumidor de eventos
        suscribirse_a_eventos_contratos_desde_reportes()
    except KeyboardInterrupt:
        logger.info("Microservicio de reportes detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el microservicio de reportes: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
