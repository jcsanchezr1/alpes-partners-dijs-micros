"""
Consumidor de eventos de contratos para el BFF.
Se suscribe al tópico eventos-contratos y mantiene una lista de contratos actualizada.
"""

import logging
import threading
import time
from typing import List, Dict, Any
from datetime import datetime

import pulsar
import _pulsar
from pulsar.schema import AvroSchema

from alpes_partners.config.settings import settings
from .schema.v1.eventos import EventoContratoCreado, EventoContratoError

logger = logging.getLogger(__name__)

class ConsumidorContratosBFF:
    """Consumidor de eventos de contratos para el BFF."""
    
    def __init__(self):
        self.ultimo_evento: Dict[str, Any] = None
        self.cliente = None
        self.consumidor = None
        self.hilo_consumidor = None
        self.ejecutando = False
        self.lock = threading.Lock()
    
    def iniciar_consumidor(self):
        """Inicia el consumidor en un hilo separado."""
        if self.ejecutando:
            logger.warning("El consumidor ya está ejecutándose")
            return
        
        self.ejecutando = True
        self.hilo_consumidor = threading.Thread(target=self._consumir_eventos, daemon=True)
        self.hilo_consumidor.start()
        logger.info("Consumidor de contratos iniciado")
    
    def detener_consumidor(self):
        """Detiene el consumidor."""
        self.ejecutando = False
        if self.hilo_consumidor:
            self.hilo_consumidor.join(timeout=5)
        if self.cliente:
            self.cliente.close()
        logger.info("Consumidor de contratos detenido")
    
    def _consumir_eventos(self):
        """Método principal del consumidor que se ejecuta en un hilo separado."""
        try:
            broker_url = settings.pulsar_address
            logger.info(f"BFF: Conectando a Pulsar en {broker_url}:6650 para eventos de contratos...")
            
            self.cliente = pulsar.Client(f'pulsar://{broker_url}:6650')
            logger.info("BFF: Cliente Pulsar creado exitosamente")
            
            # Suscribirse al tópico de eventos de contratos
            self.consumidor = self.cliente.subscribe(
                'eventos-contratos',
                consumer_type=_pulsar.ConsumerType.Shared,
                subscription_name='bff-contratos-stream',
                schema=AvroSchema(EventoContratoCreado)
            )
            
            logger.info("BFF: Suscrito exitosamente a eventos de contratos")
            logger.info("BFF: Esperando eventos en el tópico 'eventos-contratos'...")
            
            while self.ejecutando:
                try:
                    # Recibir mensaje con timeout
                    mensaje = self.consumidor.receive(timeout_millis=1000)
                    if mensaje:
                        evento = mensaje.value()
                        logger.info(f"BFF: ¡Evento de contrato recibido! ID: {getattr(evento, 'id', 'N/A')}")
                        logger.info(f"BFF: Datos del evento: {evento}")
                        
                        # Procesar evento
                        self._procesar_evento_contrato(evento)
                        
                        # Confirmar procesamiento
                        self.consumidor.acknowledge(mensaje)
                        logger.info("BFF: Evento de contrato procesado y confirmado")
                    else:
                        # Timeout - esto es normal, no es un error
                        logger.debug("BFF: Timeout esperando eventos (normal)")
                        
                except Exception as e:
                    if "timeout" not in str(e).lower() and "no message" not in str(e).lower():
                        logger.error(f"BFF: Error procesando evento de contrato: {e}")
                        import traceback
                        logger.error(f"BFF: Traceback: {traceback.format_exc()}")
                    time.sleep(0.1)  # Pequeña pausa para evitar CPU alto
                    
        except Exception as e:
            logger.error(f"BFF: Error crítico en consumidor de contratos: {e}")
            import traceback
            logger.error(f"BFF: Traceback completo: {traceback.format_exc()}")
        finally:
            if self.cliente:
                self.cliente.close()
                logger.info("BFF: Conexión con Pulsar cerrada")
    
    def _procesar_evento_contrato(self, evento):
        """Procesa un evento de contrato y actualiza el último evento."""
        try:
            with self.lock:
                # Extraer datos del evento
                datos_contrato = self._extraer_datos_contrato(evento)
                
                # Actualizar el último evento (no hacer append)
                self.ultimo_evento = datos_contrato
                
                logger.info(f"BFF: Evento actualizado: {datos_contrato.get('id_contrato', 'N/A')}")
                
        except Exception as e:
            logger.error(f"BFF: Error procesando evento de contrato: {e}")
    
    def _extraer_datos_contrato(self, evento) -> Dict[str, Any]:
        """Extrae los datos relevantes del evento de contrato."""
        datos = {}
        
        try:
            # El evento puede tener diferentes estructuras, manejamos ambos casos
            if hasattr(evento, 'data') and evento.data:
                data = evento.data
                datos = {
                    'id_contrato': str(getattr(data, 'id_contrato', '')),
                    'id_influencer': str(getattr(data, 'id_influencer', '')),
                    'id_campana': str(getattr(data, 'id_campana', '')),
                    'fecha_creacion': str(getattr(data, 'fecha_creacion', ''))
                }
            
        except Exception as e:
            logger.error(f"BFF: Error extrayendo datos del evento: {e}")
            # Datos por defecto en caso de error
            datos = {
                'id_contrato': 'unknown',
                'id_influencer': 'unknown',
                'id_campana': 'unknown',
                'fecha_creacion': datetime.utcnow().isoformat()
            }
        
        return datos
    
    def obtener_ultimo_evento(self) -> Dict[str, Any]:
        """Obtiene el último evento recibido."""
        with self.lock:
            return self.ultimo_evento.copy() if self.ultimo_evento else None

# Instancia global del consumidor
consumidor_contratos = ConsumidorContratosBFF()
