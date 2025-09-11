"""
Consumidor de eventos para el módulo de reportes.
Se suscribe a eventos de campañas y ejecuta comandos para crear reportes automáticamente.
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

from reportes.config.app import crear_app_minima
from reportes.seedwork.infraestructura import utils
from reportes.modulos.reportes.aplicacion.comandos.crear_reporte import RegistrarReporte, ejecutar_comando_registrar_reporte

# Esquema de eventos de contrato
from reportes.modulos.reportes.infraestructura.schema.eventos import EventoContratoCreado

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_eventos_contratos_desde_reportes():
    """
    Suscribirse a eventos de contratos para crear reportes automáticamente.
    """
    cliente = None
    try:
        logger.info("REPORTES: Conectando a Pulsar...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        # Consumidor para eventos de contratos
        consumidor = cliente.subscribe(
            'eventos-contratos', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='reportes-sub-eventos-contratos', 
            schema=AvroSchema(EventoContratoCreado)
        )

        logger.info("REPORTES: Suscrito a eventos de contratos")
        logger.info("REPORTES: Esperando eventos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"REPORTES: Evento recibido - {mensaje.value()}")
                
                # Procesar evento
                _procesar_evento_contrato(mensaje.value())
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("REPORTES: Evento procesado y confirmado")
                
            except Exception as e:
                logger.error(f"REPORTES: Error procesando evento: {e}")
                time.sleep(5)  # Esperar antes de continuar
                
    except Exception as e:
        logger.error(f"REPORTES: Error en consumidor: {e}")
    finally:
        if cliente:
            cliente.close()


def _procesar_evento_contrato(evento):
    """
    Procesa un evento de contrato y crea un reporte automáticamente.
    """
    with app.app_context():
        try:
            # Extraer datos del evento
            datos = _extraer_datos_evento(evento)
            
            # Solo procesar eventos de creación de contratos
            if not _es_evento_creacion_contrato(evento):
                logger.info(f"REPORTES: Evento ignorado - Tipo: {type(evento).__name__}")
                return
            
            logger.info("REPORTES: Procesando creación de contrato para generar reporte")
            
            # Crear comando para crear reporte
            comando = _crear_comando_reporte(datos)
            
            # Ejecutar comando usando la función específica del módulo
            ejecutar_comando_registrar_reporte(comando)
            
            logger.info(f"REPORTES: Reporte creado para contrato: {datos.get('id_contrato', 'N/A')}")
            
        except Exception as e:
            logger.error(f"REPORTES: Error procesando evento: {e}")
            import traceback
            logger.error(f"REPORTES: Traceback: {traceback.format_exc()}")


def _es_evento_creacion_contrato(evento):
    """
    Verifica si el evento es una creación de contrato.
    """
    tipo_evento = type(evento).__name__
    return 'ContratoCreado' in tipo_evento or 'EventoContratoCreado' in tipo_evento


def _extraer_datos_evento(evento):
    """
    Extrae los datos relevantes del evento de contrato.
    """
    datos = {}
    
    if hasattr(evento, 'data'):
        data = evento.data
        
        # Extraer campos conocidos del evento de contrato
        if hasattr(data, 'id_contrato'):
            datos['id_contrato'] = str(data.id_contrato)
        if hasattr(data, 'id_influencer'):
            datos['id_influencer'] = str(data.id_influencer)
        if hasattr(data, 'id_campana'):
            datos['id_campana'] = str(data.id_campana)
        if hasattr(data, 'monto_total'):
            datos['monto_total'] = float(data.monto_total)
        if hasattr(data, 'moneda'):
            datos['moneda'] = str(data.moneda)
        if hasattr(data, 'tipo_contrato'):
            datos['tipo_contrato'] = str(data.tipo_contrato)
        if hasattr(data, 'fecha_creacion'):
            datos['fecha_creacion'] = str(data.fecha_creacion)
    
    return datos


def _crear_comando_reporte(datos):
    """
    Crea el comando para crear un reporte basado en los datos del contrato.
    """
    fecha_actual = datetime.utcnow()
    reporte_id = str(uuid.uuid4())
    
    # Preparar datos de origen completos
    datos_origen = {
        'contrato_id': datos.get('id_contrato'),
        'influencer_id': datos.get('id_influencer'),
        'campana_id': datos.get('id_campana'),
        'monto_total': datos.get('monto_total'),
        'moneda': datos.get('moneda'),
        'tipo_contrato': datos.get('tipo_contrato'),
        'fecha_creacion': datos.get('fecha_creacion'),
        'timestamp_procesamiento': fecha_actual.isoformat()
    }
    
    # Datos adicionales para metadatos
    datos_adicionales = {
        'contrato_id': datos.get('id_contrato'),
        'influencer_id': datos.get('id_influencer'),
        'campana_id': datos.get('id_campana'),
        'timestamp_evento': fecha_actual.isoformat(),
        'fuente_evento': 'alpes-partners-contratos',
        'procesado_por': 'reportes-microservice'
    }
    
    return RegistrarReporte(
        fecha_creacion=fecha_actual.isoformat(),
        fecha_actualizacion=fecha_actual.isoformat(),
        id=reporte_id,
        nombre=f"Reporte de Contrato: {datos.get('id_contrato', 'Sin ID')}",
        descripcion=f"Reporte generado automáticamente para el contrato {datos.get('id_contrato')} - Influencer: {datos.get('id_influencer')} - Campaña: {datos.get('id_campana')}",
        tipo_reporte="contrato",
        datos_origen=datos_origen,
        origen_evento="ContratoCreado",
        estado="activo",  # Campo para manejo de compensación
        version_esquema="1.0",
        datos_adicionales=datos_adicionales,
        incluir_metricas=True,
        formato_salida="json",
        notificar_completado=True,
        campana_origen_id=datos.get('id_campana')
    )
