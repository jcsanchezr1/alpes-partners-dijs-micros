"""
Consumidor de eventos para el módulo de campanas.
Se suscribe a eventos de influencers y ejecuta comandos para crear campanas automáticamente.
"""

import logging
import time
import uuid
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Imports esenciales
import pulsar
import _pulsar
from pulsar.schema import AvroSchema

from alpes_partners.api import create_app
from alpes_partners.seedwork.infraestructura import utils
# from alpes_partners.modulos.influencers.infraestructura.schema.v1.eventos import EventoInfluencerRegistrado
from alpes_partners.modulos.campanas.aplicacion.comandos.crear_campana import RegistrarCampana, ejecutar_comando_registrar_campana

# Crear instancia de aplicación Flask para el contexto
app = create_app({'TESTING': False})


def suscribirse_a_eventos_influencers_desde_campanas():
    """
    Suscribirse a eventos de influencers para crear campanas automáticamente.
    TEMPORALMENTE DESHABILITADO - Requiere esquema de influencers
    """
    logger.info("CAMPANAS: Consumidor de eventos de influencers temporalmente deshabilitado")
    logger.info("CAMPANAS: Se requiere configurar el esquema de eventos de influencers")
    return
    
    # Código comentado temporalmente
    # cliente = None
    # try:
    #     logger.info("🔌 CAMPAnAS: Conectando a Pulsar...")
    #     cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
    #     
    #     # Consumidor para eventos de influencers
    #     consumidor = cliente.subscribe(
    #         'eventos-influencers', 
    #         consumer_type=_pulsar.ConsumerType.Shared,
    #         subscription_name='campanas-sub-eventos-influencers', 
    #         schema=AvroSchema(EventoInfluencerRegistrado)
    #     )

    #     logger.info("CAMPANAS: Suscrito a eventos de influencers")
    #     logger.info("CAMPANAS: Esperando eventos...")
    #     
    #     while True:
    #         try:
    #             mensaje = consumidor.receive()
    #             logger.info(f"CAMPANAS: Evento recibido - {mensaje.value()}")
    #             
    #             # Procesar evento
    #             _procesar_evento_influencer(mensaje.value())
    #             
    #             # Confirmar procesamiento
    #             consumidor.acknowledge(mensaje)
    #             logger.info("CAMPANAS: Evento procesado y confirmado")
    #             
    #         except Exception as e:
    #             logger.error(f"CAMPANAS: Error procesando evento: {e}")
    #             time.sleep(5)  # Esperar antes de continuar
    #             
    # except Exception as e:
    #     logger.error(f"CAMPANAS: Error en consumidor: {e}")
    # finally:
    #     if cliente:
    #         cliente.close()


def _procesar_evento_influencer(evento):
    """
    Procesa un evento de influencer y crea una campana automáticamente.
    """
    with app.app_context():
        try:
            # Extraer datos del evento
            datos = _extraer_datos_evento(evento)
            
            # Solo procesar eventos de registro de influencers
            if not _es_evento_registro(evento):
                logger.info(f"CAMPANAS: Evento ignorado - Tipo: {type(evento).__name__}")
                return
            
            logger.info("CAMPANAS: Procesando registro de influencer para crear campana")
            
            # Crear comando para registrar campana
            comando = _crear_comando_campana(datos)
            
            # Ejecutar comando usando la función específica del módulo
            ejecutar_comando_registrar_campana(comando)
            
            logger.info(f"CAMPANAS: Campana creada para influencer: {datos.get('nombre', 'N/A')}")
            
        except Exception as e:
            logger.error(f"CAMPANAS: Error procesando evento: {e}")
            import traceback
            logger.error(f"CAMPANAS: Traceback: {traceback.format_exc()}")


def _es_evento_registro(evento):
    """
    Verifica si el evento es un registro de influencer.
    """
    tipo_evento = type(evento).__name__
    return 'InfluencerRegistrado' in tipo_evento


def _extraer_datos_evento(evento):
    """
    Extrae los datos relevantes del evento.
    """
    datos = {}
    
    if hasattr(evento, 'data'):
        data = evento.data
        
        # Extraer campos conocidos
        if hasattr(data, 'id_influencer'):
            datos['id_influencer'] = str(data.id_influencer)
        if hasattr(data, 'nombre'):
            datos['nombre'] = str(data.nombre)
        if hasattr(data, 'email'):
            datos['email'] = str(data.email)
        if hasattr(data, 'categorias'):
            datos['categorias'] = [str(cat) for cat in data.categorias] if data.categorias else []
    
    return datos


def _crear_comando_campana(datos):
    """
    Crea el comando para registrar una campana basada en los datos del influencer.
    """
    fecha_actual = datetime.utcnow()
    campana_id = str(uuid.uuid4())
    
    return RegistrarCampana(
        fecha_creacion=fecha_actual.isoformat(),
        fecha_actualizacion=fecha_actual.isoformat(),
        id=campana_id,
        nombre=f"Campana de {datos.get('nombre', 'Influencer')}",
        descripcion=f"Campana generada automáticamente para el influencer {datos.get('nombre', 'N/A')}",
        tipo_comision="cpa",
        valor_comision=10.0,
        moneda="USD",
        fecha_inicio=fecha_actual.isoformat(),
        categorias_objetivo=datos.get('categorias', []),
        tipos_afiliado_permitidos=["influencer"],
        enlaces_material=[],
        imagenes_material=[],
        banners_material=[],
        metricas_minimas={},
        auto_activar=True,
        influencer_origen_id=datos.get('id_influencer')
    )