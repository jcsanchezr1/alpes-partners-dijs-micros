#!/usr/bin/env python3
"""
Script para ejecutar el microservicio de campanas.
Incluye health check y consumidor de eventos de influencers.
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
from alpes_partners.modulos.campanas.infraestructura.consumidores import suscribirse_a_eventos_influencers_desde_campanas, suscribirse_a_eventos_eliminacion_campana
from alpes_partners.modulos.campanas.infraestructura.consumidores_comandos import suscribirse_a_comandos_campanas

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
        'service': 'campanas-microservice'
    })

@app.route('/health')
def health():
    """Endpoint de salud adicional."""
    return jsonify({
        'status': 'up',
        'service': 'campanas'
    })

def start_consumer():
    """Inicia el consumidor de eventos en un hilo separado."""
    try:
        logger.info("Iniciando consumidor de eventos de influencers...")
        suscribirse_a_eventos_influencers_desde_campanas()
    except Exception as e:
        logger.error(f"Error en el consumidor de eventos: {e}")

def start_event_consumer():
    """Inicia el consumidor de eventos de eliminación en un hilo separado."""
    try:
        logger.info("Iniciando consumidor de eventos de eliminación de campaña...")
        suscribirse_a_eventos_eliminacion_campana()
    except Exception as e:
        logger.error(f"Error en el consumidor de eventos: {e}")

def start_command_consumer():
    """Inicia el consumidor de comandos en un hilo separado."""
    try:
        logger.info("Iniciando consumidor de comandos...")
        suscribirse_a_comandos_campanas()
    except Exception as e:
        logger.error(f"Error en el consumidor de comandos: {e}")

def main():
    """Función principal del microservicio."""
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("Microservicio: HTTP health check + Event consumer")
    
    # Obtener puerto de Cloud Run
    port = int(os.environ.get('PORT', 8080))
    
    try:
        # Iniciar consumidor de eventos en hilo daemon
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Consumidor de eventos iniciado")
        
        # Iniciar consumidor de eventos de eliminación en hilo daemon
        event_consumer_thread = threading.Thread(target=start_event_consumer, daemon=True)
        event_consumer_thread.start()
        logger.info("Consumidor de eventos de eliminación iniciado")
        
        # Iniciar consumidor de comandos en hilo daemon
        command_consumer_thread = threading.Thread(target=start_command_consumer, daemon=True)
        command_consumer_thread.start()
        logger.info("Consumidor de comandos iniciado")
        
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
