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

from alpes_partners.config.app import crear_app_minima
from alpes_partners.seedwork.infraestructura import utils
from alpes_partners.modulos.campanas.infraestructura.schema.eventos import EventoInfluencerRegistrado
from alpes_partners.modulos.campanas.aplicacion.comandos.crear_campana import RegistrarCampana, ejecutar_comando_registrar_campana
from alpes_partners.modulos.campanas.aplicacion.comandos.eliminar_campana import EliminarCampana, ejecutar_comando_eliminar_campana

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_eventos_influencers_desde_campanas():
    """
    DESHABILITADO: Suscribirse a eventos de influencers para crear campanas automáticamente.
    Ahora las campañas se crean solo a través de comandos de la saga.
    """
    logger.info("CAMPANAS: Consumidor directo de influencers DESHABILITADO - Solo procesar comandos de saga")
    return
    
    # CÓDIGO COMENTADO - Las campañas ahora se crean solo a través de comandos de la saga
    # cliente = None
    # try:
    #     logger.info("CAMPANAS: Conectando a Pulsar...")
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


def suscribirse_a_eventos_eliminacion_campana():
    """
    Suscribirse a eventos de eliminación de campaña para compensación.
    """
    cliente = None
    try:
        logger.info("CAMPANAS: Conectando a Pulsar para eventos de eliminación de campaña...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        # Importar esquema de eventos
        from alpes_partners.modulos.campanas.infraestructura.schema.eventos import EventoCampanaEliminacionRequerida
        
        # Consumidor para eventos de eliminación de campaña
        consumidor = cliente.subscribe(
            'eventos-campanas-eliminacion-v2', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='campanas-sub-eventos-eliminacion-v2', 
            schema=AvroSchema(EventoCampanaEliminacionRequerida)
        )

        logger.info("CAMPANAS: Suscrito a eventos de eliminación de campaña")
        logger.info("CAMPANAS: Esperando eventos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"CAMPANAS: Evento recibido - {mensaje.value()}")
                
                # Procesar evento
                _procesar_evento_eliminacion_campana(mensaje.value())
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("CAMPANAS: Evento procesado y confirmado")
                
            except Exception as e:
                logger.error(f"CAMPANAS: Error procesando evento: {e}")
                time.sleep(5)  # Esperar antes de continuar
                
    except Exception as e:
        logger.error(f"CAMPANAS: Error en consumidor de eventos: {e}")
    finally:
        if cliente:
            cliente.close()


def _procesar_evento_eliminacion_campana(evento):
    """
    Procesa un evento de eliminación de campaña requerida.
    """
    with app.app_context():
        try:
            logger.info("CAMPANAS: Procesando evento de eliminación de campaña")
            
            # Extraer datos del evento
            if hasattr(evento, 'data'):
                data = evento.data
                logger.info(f"CAMPANAS: Datos del evento: {data}")
                
                # Crear comando de eliminar campaña desde el evento de integración
                comando = EliminarCampana(
                    campana_id=str(data.campana_id),
                    influencer_id=str(data.influencer_id),
                    razon=str(data.razon)
                )
                
                logger.info(f"CAMPANAS: Comando EliminarCampana creado desde evento:")
                logger.info(f"  - Campaña ID: {comando.campana_id}")
                logger.info(f"  - Influencer ID: {comando.influencer_id}")
                logger.info(f"  - Razón: {comando.razon}")
                
                # Ejecutar comando de dominio
                ejecutar_comando_eliminar_campana(comando)
                
                logger.info(f"CAMPANAS: Campaña {comando.campana_id} eliminada exitosamente por compensación")
                
            else:
                logger.error("CAMPANAS: Evento sin datos válidos")
                
        except Exception as e:
            logger.error(f"CAMPANAS: Error procesando evento de eliminación de campaña: {e}")
            import traceback
            logger.error(f"CAMPANAS: Traceback: {traceback.format_exc()}")


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
    logger.info(f"CAMPANAS CONSUMIDOR: Extrayendo datos del evento de influencer")
    logger.info(f"  - Tipo de evento: {type(evento)}")
    logger.info(f"  - Evento completo: {evento}")
    
    datos = {}
    
    if hasattr(evento, 'data'):
        data = evento.data
        logger.info(f"  - Datos del evento: {data}")
        logger.info(f"  - Tipo de datos: {type(data)}")
        
        # Extraer campos conocidos
        if hasattr(data, 'id_influencer'):
            datos['id_influencer'] = str(data.id_influencer)
            logger.info(f"  - id_influencer extraído: {datos['id_influencer']}")
        if hasattr(data, 'nombre'):
            datos['nombre'] = str(data.nombre)
            logger.info(f"  - nombre extraído: {datos['nombre']}")
        if hasattr(data, 'email'):
            datos['email'] = str(data.email)
            logger.info(f"  - email extraído: {datos['email']}")
        if hasattr(data, 'categorias'):
            datos['categorias'] = [str(cat) for cat in data.categorias] if data.categorias else []
            logger.info(f"  - categorias extraídas: {datos['categorias']}")
    
    logger.info(f"CAMPANAS CONSUMIDOR: Datos finales extraídos: {datos}")
    return datos


def _crear_comando_campana(datos):
    """
    Crea el comando para registrar una campana basada en los datos del influencer.
    """
    from datetime import timedelta
    
    logger.info(f"CAMPANAS CONSUMIDOR: Creando comando con datos: {datos}")
    
    fecha_actual = datetime.utcnow()
    fecha_fin_automatica = fecha_actual + timedelta(days=30)  # 30 días de duración
    campana_id = str(uuid.uuid4())
    
    logger.info(f"CAMPANAS CONSUMIDOR: Creando comando con:")
    logger.info(f"  - influencer_origen_id: {datos.get('id_influencer')}")
    logger.info(f"  - influencer_origen_nombre: {datos.get('nombre')}")
    logger.info(f"  - influencer_origen_email: {datos.get('email')}")
    logger.info(f"  - fecha_inicio: {fecha_actual.isoformat()}")
    logger.info(f"  - fecha_fin: {fecha_fin_automatica.isoformat()} (30 días de duración)")
    
    # Crear nombre único usando el UUID completo para evitar duplicados
    nombre_unico = f"Campana de {datos.get('nombre', 'Influencer')} - {campana_id}"
    logger.info(f"  - nombre_campana: {nombre_unico}")
    logger.info(f"  - campana_id: {campana_id}")
    
    return RegistrarCampana(
        fecha_creacion=fecha_actual.isoformat(),
        fecha_actualizacion=fecha_actual.isoformat(),
        id=campana_id,
        nombre=nombre_unico,
        descripcion=f"Campana generada automáticamente para el influencer {datos.get('nombre', 'N/A')}",
        tipo_comision="cpa",
        valor_comision=10.0,
        moneda="USD",
        fecha_inicio=fecha_actual.isoformat(),
        fecha_fin=fecha_fin_automatica.isoformat(),  # Agregar fecha de fin automática
        categorias_objetivo=datos.get('categorias', []),
        tipos_afiliado_permitidos=["influencer"],
        enlaces_material=[],
        imagenes_material=[],
        banners_material=[],
        metricas_minimas={},
        auto_activar=True,
        influencer_origen_id=datos.get('id_influencer'),
        # Datos del influencer para el evento
        influencer_origen_nombre=datos.get('nombre'),
        influencer_origen_email=datos.get('email')
    )