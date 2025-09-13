"""
Consumidor de eventos para el módulo de influencers.
Se suscribe a eventos de crear influencer y ejecuta comandos para registrar influencers automáticamente.
"""

import logging
import time
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Imports esenciales
import pulsar
import _pulsar
from pulsar.schema import AvroSchema

from alpes_partners.config.app import crear_app_minima
from alpes_partners.seedwork.infraestructura import utils
from alpes_partners.modulos.influencers.aplicacion.comandos.registrar_influencer import RegistrarInfluencer, ejecutar_comando_registrar_influencer

# Esquema de eventos de crear influencer
from alpes_partners.modulos.influencers.infraestructura.schema.v1.crear_influencer import EventoCrearInfluencer

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_eventos_crear_influencer():
    """
    Suscribirse a eventos de crear influencer para registrar influencers automáticamente.
    """
    cliente = None
    try:
        logger.info("INFLUENCERS: Conectando a Pulsar...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        # Consumidor para eventos de crear influencer
        consumidor = cliente.subscribe(
            'eventos-crear-influencer', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='influencers-sub-crear-influencer', 
            schema=AvroSchema(EventoCrearInfluencer)
        )

        logger.info("INFLUENCERS: Suscrito a eventos de crear influencer")
        logger.info("INFLUENCERS: Esperando eventos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"INFLUENCERS: Evento recibido - {mensaje.value()}")
                
                # Procesar evento
                _procesar_evento_crear_influencer(mensaje.value())
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("INFLUENCERS: Evento procesado y confirmado")
                
            except Exception as e:
                logger.error(f"INFLUENCERS: Error procesando evento: {e}")
                time.sleep(5)  # Esperar antes de continuar
                
    except Exception as e:
        logger.error(f"INFLUENCERS: Error en consumidor: {e}")
    finally:
        if cliente:
            cliente.close()


def _procesar_evento_crear_influencer(evento):
    """
    Procesa un evento de crear influencer y ejecuta el comando para registrar el influencer.
    """
    with app.app_context():
        try:
            # Extraer datos del evento
            datos = _extraer_datos_evento(evento)
            
            # Solo procesar eventos de crear influencer
            if not _es_evento_crear_influencer(evento):
                logger.info(f"INFLUENCERS: Evento ignorado - Tipo: {type(evento).__name__}")
                return
            
            logger.info("INFLUENCERS: Procesando creación de influencer")
            
            # Crear comando para registrar influencer
            comando = _crear_comando_influencer(datos)
            
            # Ejecutar comando usando la función específica del módulo
            ejecutar_comando_registrar_influencer(comando)
            
            logger.info(f"INFLUENCERS: Influencer creado: {datos.get('id', 'N/A')}")
            
        except Exception as e:
            logger.error(f"INFLUENCERS: Error procesando evento: {e}")
            import traceback
            logger.error(f"INFLUENCERS: Traceback: {traceback.format_exc()}")


def _es_evento_crear_influencer(evento):
    """
    Verifica si el evento es de crear influencer.
    """
    tipo_evento = type(evento).__name__
    return 'CrearInfluencer' in tipo_evento or 'EventoCrearInfluencer' in tipo_evento


def _extraer_datos_evento(evento):
    """
    Extrae los datos relevantes del evento de crear influencer.
    """
    datos = {}
    
    if hasattr(evento, 'data'):
        data = evento.data
        
        # Extraer campos conocidos del evento de crear influencer
        if hasattr(data, 'id'):
            datos['id'] = str(data.id)
        if hasattr(data, 'nombre'):
            datos['nombre'] = str(data.nombre)
        if hasattr(data, 'email'):
            datos['email'] = str(data.email)
        if hasattr(data, 'categorias'):
            # Convertir lista de categorías
            datos['categorias'] = list(data.categorias) if data.categorias else []
        if hasattr(data, 'descripcion') and data.descripcion:
            datos['descripcion'] = str(data.descripcion)
        if hasattr(data, 'biografia') and data.biografia:
            datos['biografia'] = str(data.biografia)
        if hasattr(data, 'sitio_web') and data.sitio_web:
            datos['sitio_web'] = str(data.sitio_web)
        if hasattr(data, 'telefono') and data.telefono:
            datos['telefono'] = str(data.telefono)
        if hasattr(data, 'fecha_creacion'):
            datos['fecha_creacion'] = str(data.fecha_creacion)
        if hasattr(data, 'fecha_actualizacion'):
            datos['fecha_actualizacion'] = str(data.fecha_actualizacion)
    
    return datos


def _crear_comando_influencer(datos):
    """
    Crea el comando para registrar un influencer basado en los datos del evento.
    """
    return RegistrarInfluencer(
        id=datos.get('id'),
        nombre=datos.get('nombre'),
        email=datos.get('email'),
        categorias=datos.get('categorias', []),
        descripcion=datos.get('descripcion'),
        biografia=datos.get('biografia'),
        sitio_web=datos.get('sitio_web'),
        telefono=datos.get('telefono'),
        fecha_creacion=datos.get('fecha_creacion'),
        fecha_actualizacion=datos.get('fecha_actualizacion')
    )
