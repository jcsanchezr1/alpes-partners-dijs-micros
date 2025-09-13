#!/usr/bin/env python3
"""
Script para ejecutar el microservicio de influencers.
NOTA: Influencers es completamente asíncrono, solo consume eventos.
Incluye health check mínimo para compatibilidad con Cloud Run.
"""

import sys
import os
import threading
from flask import Flask, jsonify

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

import logging
from alpes_partners.config.settings import settings
from alpes_partners.modulos.influencers.infraestructura.consumidores import suscribirse_a_eventos_crear_influencer

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear aplicación Flask mínima
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check para Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'service': 'influencers-microservice'
    })

def start_consumer():
    """Inicia el consumidor de eventos en un hilo separado."""
    try:
        logger.info("Iniciando consumidor de eventos...")
        suscribirse_a_eventos_crear_influencer()
    except Exception as e:
        logger.error(f"Error en el consumidor de eventos: {e}")

def main():
    """Función principal del microservicio."""
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("Microservicio: HTTP health check + Event consumer")
    
    # Obtener puerto de Cloud Run
    port = int(os.environ.get('PORT', 8080))
    
    try:
        # Iniciar consumidor en hilo daemon
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Consumidor de eventos iniciado")
        
        # Iniciar servidor HTTP
        logger.info(f"Servidor HTTP iniciado en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Microservicio detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el microservicio: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
