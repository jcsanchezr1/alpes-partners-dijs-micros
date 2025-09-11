#!/usr/bin/env python3
"""Script para ejecutar el consumidor de eventos Pulsar del microservicio de reportes."""

import sys
import os
import logging

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from reportes.config.settings import settings
from reportes.modulos.reportes.infraestructura.consumidores import suscribirse_a_eventos_contratos_desde_reportes

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal del consumidor."""
    logger.info(f"Iniciando consumidor de eventos para {settings.app_name}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info("Conectando a Pulsar...")
    
    try:
        # Iniciar el consumidor de eventos
        suscribirse_a_eventos_contratos_desde_reportes()
    except KeyboardInterrupt:
        logger.info("Consumidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el consumidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
