#!/usr/bin/env python3
"""
Script para ejecutar el coordinador de saga.
La saga orquesta el flujo completo: Influencers → Campañas → Contratos.
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
from alpes_partners.modulos.sagas.infraestructura.consumidores import suscribirse_a_eventos_saga

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear aplicación Flask mínima para health check
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check para Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'service': 'saga-coordinator',
        'description': 'Orquestador de saga para Influencers → Campañas → Contratos'
    })

@app.route('/health')
def health():
    """Health check adicional."""
    return jsonify({'status': 'ok', 'service': 'saga'})

def start_saga_consumers():
    """Inicia los consumidores de la saga en un hilo separado."""
    try:
        logger.info("SAGA: Iniciando consumidores de eventos...")
        suscribirse_a_eventos_saga()
    except Exception as e:
        logger.error(f"SAGA: Error en los consumidores de eventos: {e}")

def main():
    """Función principal del coordinador de saga."""
    logger.info(f"SAGA: Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("SAGA: Coordinador de saga - HTTP health check + Event consumers")
    
    # Obtener puerto de Cloud Run
    port = int(os.environ.get('PORT', 8084))  # Puerto único para la saga
    
    try:
        # Iniciar consumidores en hilo daemon
        consumer_thread = threading.Thread(target=start_saga_consumers, daemon=True)
        consumer_thread.start()
        logger.info("SAGA: Consumidores de eventos iniciados")
        
        # Iniciar servidor HTTP para health check
        logger.info(f"SAGA: Servidor HTTP iniciado en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        logger.info("SAGA: Coordinador detenido por el usuario")
    except Exception as e:
        logger.error(f"SAGA: Error en el coordinador: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
