"""
Servicios para streaming de contratos en tiempo real.
"""

import logging
import threading
import time
from typing import List, Dict, Any, Generator
from datetime import datetime

from ..infraestructura.consumidor import consumidor_contratos

logger = logging.getLogger(__name__)

class ServicioStreamingContratos:
    """Servicio para manejar el streaming de contratos en tiempo real."""
    
    def __init__(self):
        self.clientes_conectados: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def iniciar_consumidor(self):
        """Inicia el consumidor de eventos de contratos."""
        try:
            consumidor_contratos.iniciar_consumidor()
            logger.info("Servicio de streaming de contratos iniciado")
        except Exception as e:
            logger.error(f"Error iniciando consumidor de contratos: {e}")
            raise
    
    def detener_consumidor(self):
        """Detiene el consumidor de eventos de contratos."""
        try:
            consumidor_contratos.detener_consumidor()
            logger.info("Servicio de streaming de contratos detenido")
        except Exception as e:
            logger.error(f"Error deteniendo consumidor de contratos: {e}")
    
    def obtener_ultimo_evento(self) -> Dict[str, Any]:
        """Obtiene el último evento recibido."""
        return consumidor_contratos.obtener_ultimo_evento()
    
    def generar_stream_eventos(self) -> Generator[Dict[str, Any], None, None]:
        """
        Genera un stream de eventos en tiempo real.
        Utiliza Server-Sent Events (SSE) para enviar actualizaciones.
        """
        logger.info("Iniciando stream de eventos")
        
        try:
            # Mantener conexión activa y enviar eventos individuales
            ultimo_evento_enviado = None
            while True:
                try:
                    # Verificar si hay un nuevo evento
                    evento_actual = self.obtener_ultimo_evento()
                    
                    if evento_actual and evento_actual != ultimo_evento_enviado:
                        # Enviar el evento individual directamente en data
                        yield {
                            'data': evento_actual
                        }
                        
                        # Actualizar referencia al último evento enviado
                        ultimo_evento_enviado = evento_actual
                    
                    # Pausa para evitar CPU alto
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error en stream de eventos: {e}")
                    time.sleep(1)
                    
        except GeneratorExit:
            logger.info("Cliente desconectado del stream de eventos")

# Instancia global del servicio
servicio_streaming = ServicioStreamingContratos()
