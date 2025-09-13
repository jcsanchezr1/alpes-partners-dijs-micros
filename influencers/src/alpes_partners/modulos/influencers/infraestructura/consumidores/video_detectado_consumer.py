"""
Consumidor de eventos para videos detectados.
Se suscribe al tópico video-detectado y procesa los eventos.
"""

import logging
import time
from typing import Dict, Any

# Configurar logging
logger = logging.getLogger(__name__)

# Imports esenciales
import pulsar
import _pulsar
from pulsar.schema import AvroSchema

from alpes_partners.api import create_app
from alpes_partners.seedwork.infraestructura import utils
from alpes_partners.modulos.influencers.infraestructura.schema.v1.video_detectado import EventoVideoDetectado
from alpes_partners.modulos.influencers.aplicacion.handlers.video_detectado_handler import procesar_evento_video_detectado

# Crear instancia de aplicación Flask para el contexto
app = create_app({'TESTING': False})


def suscribirse_a_videos_detectados():
    """
    Suscribirse a eventos de videos detectados.
    """
    cliente = None
    try:
        logger.info("🔌 VIDEO CONSUMER: Conectando a Pulsar...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        # Consumidor para eventos de videos detectados
        consumidor = cliente.subscribe(
            'video-detectado', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='influencers-sub-video-detectado', 
            schema=AvroSchema(EventoVideoDetectado)
        )

        logger.info("VIDEO CONSUMER: Suscrito a eventos de videos detectados")
        logger.info("VIDEO CONSUMER: Esperando eventos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"VIDEO CONSUMER: Evento recibido - {mensaje.value()}")
                
                # Procesar evento
                _procesar_evento_video(mensaje.value())
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("VIDEO CONSUMER: Evento procesado y confirmado")
                
            except Exception as e:
                logger.error(f"VIDEO CONSUMER: Error procesando evento: {e}")
                time.sleep(5)  # Esperar antes de continuar
                
    except Exception as e:
        logger.error(f"VIDEO CONSUMER: Error en consumidor: {e}")
    finally:
        if cliente:
            cliente.close()


def _procesar_evento_video(evento):
    """
    Procesa un evento de video detectado.
    
    Args:
        evento: Evento de video detectado
    """
    with app.app_context():
        try:
            logger.info("VIDEO CONSUMER: Procesando evento de video detectado")
            
            # Convertir evento a diccionario para el handler
            evento_data = {
                'id': evento.id,
                'id_entidad': evento.id_entidad,
                'fecha_evento': evento.fecha_evento,
                'version': evento.version,
                'data': {
                    'video_id': evento.data.video_id,
                    'influencer_id': evento.data.influencer_id,
                    'plataforma': evento.data.plataforma,
                    'url_video': evento.data.url_video,
                    'titulo': evento.data.titulo,
                    'descripcion': evento.data.descripcion,
                    'duracion_segundos': evento.data.duracion_segundos,
                    'fecha_deteccion': evento.data.fecha_deteccion,
                    'metadatos': evento.data.metadatos,
                    # Datos del influencer
                    'influencer_nombre': evento.data.influencer_nombre,
                    'influencer_email': evento.data.influencer_email,
                    'influencer_categorias': evento.data.influencer_categorias,
                    'influencer_descripcion': evento.data.influencer_descripcion,
                    'influencer_biografia': evento.data.influencer_biografia,
                    'influencer_sitio_web': evento.data.influencer_sitio_web,
                    'influencer_telefono': evento.data.influencer_telefono
                }
            }
            
            # Procesar el evento
            procesar_evento_video_detectado(evento_data)
            
            logger.info(f"VIDEO CONSUMER: Video procesado exitosamente - Video ID: {evento.data.video_id}")
            
        except Exception as e:
            logger.error(f"VIDEO CONSUMER: Error procesando evento: {e}")
            import traceback
            logger.error(f"VIDEO CONSUMER: Traceback: {traceback.format_exc()}")


def _es_evento_video_detectado(evento) -> bool:
    """
    Verifica si el evento es de video detectado.
    
    Args:
        evento: Evento a verificar
        
    Returns:
        bool: True si es evento de video detectado
    """
    return hasattr(evento, 'data') and hasattr(evento.data, 'video_id')
