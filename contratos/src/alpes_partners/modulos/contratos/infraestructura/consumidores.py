"""
Consumidor de eventos para el módulo de contratos.
Se suscribe a eventos de campañas y ejecuta comandos para crear contratos automáticamente.
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
from alpes_partners.modulos.contratos.aplicacion.comandos.crear_contrato import CrearContrato, ejecutar_comando_crear_contrato

# Definir esquema de campaña localmente para evitar dependencias circulares
from pulsar.schema import Record, String, Array, Float

class CampanaCreadaPayload(Record):
    """Payload del evento de campaña creada - debe coincidir con el esquema de campanas."""
    campana_id = String()
    nombre = String()
    descripcion = String()
    tipo_comision = String()
    valor_comision = Float()
    moneda = String(default="USD")
    categorias_objetivo = Array(String())
    fecha_inicio = String()
    fecha_fin = String(default=None, required=False)
    # Campos adicionales para crear contratos
    influencer_id = String(default=None, required=False)
    influencer_nombre = String(default=None, required=False)
    influencer_email = String(default=None, required=False)
    monto_base = Float(default=None, required=False)
    entregables = String(default=None, required=False)
    tipo_contrato = String(default="puntual")
    fecha_creacion = String()

class EventoCampanaCreada(Record):
    """Evento de integración para campaña creada - debe coincidir con el esquema de campanas."""
    data = CampanaCreadaPayload()

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_eventos_campanas_desde_contratos():
    """
    DESHABILITADO: Suscribirse a eventos de campañas para crear contratos automáticamente.
    Ahora los contratos se crean solo a través de comandos de la saga.
    """
    logger.info("CONTRATOS: Consumidor directo de campañas DESHABILITADO - Solo procesar comandos de saga")
    return
    
    # CÓDIGO COMENTADO - Los contratos ahora se crean solo a través de comandos de la saga
    # cliente = None
    # try:
    #     logger.info("CONTRATOS: Conectando a Pulsar...")
    #     cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
    #     
    #     # Consumidor para eventos de campañas
    #     consumidor = cliente.subscribe(
    #         'eventos-campanas', 
    #         consumer_type=_pulsar.ConsumerType.Shared,
    #         subscription_name='contratos-sub-eventos-campanas', 
    #         schema=AvroSchema(EventoCampanaCreada)
    #     )

    #     logger.info("CONTRATOS: Suscrito a eventos de campañas")
    #     logger.info("CONTRATOS: Esperando eventos...")
    #     
    #     while True:
    #         try:
    #             mensaje = consumidor.receive()
    #             logger.info(f"CONTRATOS: Evento recibido - {mensaje.value()}")
    #             
    #             # Procesar evento
    #             _procesar_evento_campana(mensaje.value())
    #             
    #             # Confirmar procesamiento
    #             consumidor.acknowledge(mensaje)
    #             logger.info("CONTRATOS: Evento procesado y confirmado")
    #             
    #         except Exception as e:
    #             logger.error(f"CONTRATOS: Error procesando evento: {e}")
    #             time.sleep(5)  # Esperar antes de continuar
    #             
    # except Exception as e:
    #     logger.error(f"CONTRATOS: Error en consumidor: {e}")
    # finally:
    #     if cliente:
    #         cliente.close()


def _procesar_evento_campana(evento):
    """
    Procesa un evento de campaña y crea un contrato automáticamente.
    """
    with app.app_context():
        try:
            # Extraer datos del evento
            datos = _extraer_datos_evento(evento)
            
            # Solo procesar eventos de creación de campañas
            if not _es_evento_creacion_campana(evento):
                logger.info(f"CONTRATOS: Evento ignorado - Tipo: {type(evento).__name__}")
                return
            
            logger.info("CONTRATOS: Procesando creación de campaña para generar contrato")
            
            # Crear comando para crear contrato
            comando = _crear_comando_contrato(datos)
            
            # Ejecutar comando usando la función específica del módulo
            ejecutar_comando_crear_contrato(comando)
            
            logger.info(f"CONTRATOS: Contrato creado para campaña: {datos.get('id_campana', 'N/A')}")
            
        except Exception as e:
            logger.error(f"CONTRATOS: Error procesando evento: {e}")
            import traceback
            logger.error(f"CONTRATOS: Traceback: {traceback.format_exc()}")
            
            # Publicar evento de error para el saga
            _publicar_evento_error_contrato(evento, str(e))


def _es_evento_creacion_campana(evento):
    """
    Verifica si el evento es una creación de campaña.
    """
    tipo_evento = type(evento).__name__
    return 'CampanaCreada' in tipo_evento or 'EventoCampanaCreada' in tipo_evento


def _extraer_datos_evento(evento):
    """
    Extrae los datos relevantes del evento de campaña.
    """
    datos = {}
    
    if hasattr(evento, 'data'):
        data = evento.data
        
        # DEBUG: Mostrar datos crudos del evento
        logger.info(f"CONTRATOS CONSUMIDOR: Datos crudos del evento:")
        logger.info(f"  - fecha_inicio: {getattr(data, 'fecha_inicio', 'N/A')} (tipo: {type(getattr(data, 'fecha_inicio', None))})")
        logger.info(f"  - fecha_fin: {getattr(data, 'fecha_fin', 'N/A')} (tipo: {type(getattr(data, 'fecha_fin', None))})")
        logger.info(f"  - influencer_email: {getattr(data, 'influencer_email', 'N/A')} (tipo: {type(getattr(data, 'influencer_email', None))})")
        
        # Extraer campos del evento de campaña
        if hasattr(data, 'campana_id'):
            datos['id_campana'] = str(data.campana_id)
        if hasattr(data, 'nombre'):
            datos['nombre_campana'] = str(data.nombre)
        if hasattr(data, 'influencer_id'):
            datos['id_influencer'] = str(data.influencer_id)
        if hasattr(data, 'influencer_nombre'):
            datos['nombre_influencer'] = str(data.influencer_nombre)
        if hasattr(data, 'influencer_email'):
            datos['email_influencer'] = str(data.influencer_email)
        if hasattr(data, 'categorias_objetivo'):
            datos['categorias'] = data.categorias_objetivo if hasattr(data.categorias_objetivo, '__iter__') else [str(data.categorias_objetivo)]
        if hasattr(data, 'descripcion'):
            datos['descripcion'] = str(data.descripcion)
        if hasattr(data, 'monto_base'):
            datos['monto_base'] = float(data.monto_base)
        if hasattr(data, 'moneda'):
            datos['moneda'] = str(data.moneda)
        if hasattr(data, 'fecha_inicio'):
            datos['fecha_inicio'] = str(data.fecha_inicio)
        if hasattr(data, 'fecha_fin'):
            datos['fecha_fin'] = str(data.fecha_fin) if data.fecha_fin else None
        if hasattr(data, 'entregables'):
            datos['entregables'] = str(data.entregables)
        if hasattr(data, 'tipo_contrato'):
            datos['tipo_contrato'] = str(data.tipo_contrato)
        if hasattr(data, 'fecha_creacion'):
            datos['fecha_creacion'] = str(data.fecha_creacion)
    
    return datos


def _crear_comando_contrato(datos):
    """
    Crea el comando para crear un contrato basado en los datos de la campaña.
    """
    fecha_actual = datetime.utcnow()
    contrato_id = str(uuid.uuid4())
    
    return CrearContrato(
        fecha_creacion=fecha_actual.isoformat(),
        fecha_actualizacion=fecha_actual.isoformat(),
        id=contrato_id,
        influencer_id=datos.get('id_influencer', ''),
        influencer_nombre=datos.get('nombre_influencer', ''),
        influencer_email=datos.get('email_influencer', ''),
        campana_id=datos.get('id_campana', ''),
        campana_nombre=datos.get('nombre_campana', ''),
        categorias=datos.get('categorias', []),
        descripcion=datos.get('descripcion', ''),
        monto_base=datos.get('monto_base', 0.0),
        moneda=datos.get('moneda', 'USD'),
        fecha_inicio=datos.get('fecha_inicio'),
        fecha_fin=datos.get('fecha_fin'),
        entregables=datos.get('entregables'),
        tipo_contrato=datos.get('tipo_contrato', 'puntual')
    )


def _publicar_evento_error_contrato(evento_campana, error: str):
    """Publica un evento de error cuando falla la creación del contrato."""
    try:
        from alpes_partners.modulos.contratos.infraestructura.despachadores import DespachadorContratos
        import uuid
        from datetime import datetime
        
        logger.info(f"CONTRATOS: Publicando evento de error de contrato")
        
        # Extraer datos del evento de campaña
        datos = _extraer_datos_evento(evento_campana)
        
        # Crear objeto evento de error con los datos necesarios
        class EventoErrorContrato:
            def __init__(self, datos, error):
                self.id = str(uuid.uuid4())
                self.contrato_id = str(uuid.uuid4())
                self.influencer_id = datos.get('id_influencer', '')
                self.campana_id = datos.get('id_campana', '')
                self.monto_total = datos.get('monto_base', 0.0)
                self.moneda = datos.get('moneda', 'USD')
                self.tipo_contrato = datos.get('tipo_contrato', 'puntual')
                self.fecha_creacion = datetime.utcnow()
                self.error = error
                self.error_detalle = f"Error al crear contrato para campaña {datos.get('id_campana', 'N/A')}: {error}"
        
        evento_error = EventoErrorContrato(datos, error)
        
        # Publicar evento usando el método específico para errores
        despachador = DespachadorContratos()
        despachador.publicar_evento_error_contrato(evento_error, "eventos-contratos-error")
        
        logger.info(f"CONTRATOS: Evento de error publicado exitosamente en tópico eventos-contratos-error")
        
    except Exception as e:
        logger.error(f"CONTRATOS: Error publicando evento de error: {e}")
        import traceback
        logger.error(f"CONTRATOS: Traceback: {traceback.format_exc()}")
