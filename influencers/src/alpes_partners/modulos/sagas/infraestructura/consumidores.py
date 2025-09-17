"""
Consumidor de eventos para la saga.
Se suscribe a eventos de influencers, campañas y contratos para orquestar el flujo completo.
"""

import logging
import time
import threading
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Imports esenciales
import pulsar
import _pulsar
from pulsar.schema import AvroSchema, Record, String, Array, Float, Long

from alpes_partners.config.app import crear_app_minima
from alpes_partners.seedwork.infraestructura import utils

# Importar eventos de dominio de los diferentes módulos
from ..dominio.eventos import CampanaCreada, ContratoCreado
from ...influencers.dominio.eventos import InfluencerRegistrado

# Importar coordinador de saga
from ..aplicacion.coordinadores.saga_reservas import oir_mensaje

# Definir esquemas de eventos (compatible con los microservicios)
class InfluencerRegistradoPayload(Record):
    """Payload del evento InfluencerRegistrado."""
    id_influencer = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    fecha_registro = Long()

class EventoInfluencerRegistrado(Record):
    """Evento de integración para influencer registrado."""
    data = InfluencerRegistradoPayload()

class CampanaCreadaPayload(Record):
    """Payload del evento CampanaCreada."""
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
    """Evento de integración para campaña creada."""
    data = CampanaCreadaPayload()

class ContratoCreadoPayload(Record):
    """Payload del evento ContratoCreado."""
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String(default="USD")
    tipo_contrato = String()
    fecha_creacion = String()

class EventoContratoCreado(Record):
    """Evento de integración para contrato creado."""
    data = ContratoCreadoPayload()

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_eventos_saga():
    """
    Función principal que inicia los tres consumidores de la saga en paralelo.
    """
    logger.info("SAGA: Iniciando consumidores de eventos...")
    
    # Crear hilos para cada consumidor
    threads = []
    
    # Hilo para eventos de influencers
    thread_influencers = threading.Thread(
        target=_consumir_eventos_influencers,
        name="saga-influencers-consumer",
        daemon=True
    )
    threads.append(thread_influencers)
    
    # Hilo para eventos de campañas
    thread_campanas = threading.Thread(
        target=_consumir_eventos_campanas,
        name="saga-campanas-consumer", 
        daemon=True
    )
    threads.append(thread_campanas)
    
    # Hilo para eventos de contratos
    thread_contratos = threading.Thread(
        target=_consumir_eventos_contratos,
        name="saga-contratos-consumer",
        daemon=True
    )
    threads.append(thread_contratos)
    
    # Iniciar todos los hilos
    for thread in threads:
        thread.start()
        logger.info(f"SAGA: Iniciado hilo {thread.name}")
    
    # Esperar a que todos los hilos terminen
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("SAGA: Deteniendo consumidores...")


def _consumir_eventos_influencers():
    """
    Consumidor específico para eventos de influencers.
    """
    cliente = None
    try:
        logger.info("SAGA: Conectando a Pulsar para eventos de influencers...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        consumidor = cliente.subscribe(
            'eventos-influencers',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='saga-sub-eventos-influencers',
            schema=AvroSchema(EventoInfluencerRegistrado)
        )

        logger.info("SAGA: Suscrito a eventos de influencers")
        logger.info("SAGA: Esperando eventos de influencers...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"SAGA: Evento de influencer recibido - {mensaje.value()}")
                
                # Convertir evento Pulsar a evento de dominio
                evento_dominio = _convertir_evento_influencer(mensaje.value())
                
                # Procesar con la saga
                with app.app_context():
                    oir_mensaje(evento_dominio)
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("SAGA: Evento de influencer procesado y confirmado")
                
            except Exception as e:
                logger.error(f"SAGA: Error procesando evento de influencer: {e}")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"SAGA: Error en consumidor de influencers: {e}")
    finally:
        if cliente:
            cliente.close()


def _consumir_eventos_campanas():
    """
    Consumidor específico para eventos de campañas.
    """
    cliente = None
    try:
        logger.info("SAGA: Conectando a Pulsar para eventos de campañas...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        consumidor = cliente.subscribe(
            'eventos-campanas',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='saga-sub-eventos-campanas',
            schema=AvroSchema(EventoCampanaCreada)
        )

        logger.info("SAGA: Suscrito a eventos de campañas")
        logger.info("SAGA: Esperando eventos de campañas...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"SAGA: Evento de campaña recibido - {mensaje.value()}")
                
                # Convertir evento Pulsar a evento de dominio
                evento_dominio = _convertir_evento_campana(mensaje.value())
                
                # Procesar con la saga
                with app.app_context():
                    oir_mensaje(evento_dominio)
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("SAGA: Evento de campaña procesado y confirmado")
                
            except Exception as e:
                logger.error(f"SAGA: Error procesando evento de campaña: {e}")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"SAGA: Error en consumidor de campañas: {e}")
    finally:
        if cliente:
            cliente.close()


def _consumir_eventos_contratos():
    """
    Consumidor específico para eventos de contratos.
    """
    cliente = None
    try:
        logger.info("SAGA: Conectando a Pulsar para eventos de contratos...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        consumidor = cliente.subscribe(
            'eventos-contratos',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='saga-sub-eventos-contratos',
            schema=AvroSchema(EventoContratoCreado)
        )

        logger.info("SAGA: Suscrito a eventos de contratos")
        logger.info("SAGA: Esperando eventos de contratos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"SAGA: Evento de contrato recibido - {mensaje.value()}")
                
                # Convertir evento Pulsar a evento de dominio
                evento_dominio = _convertir_evento_contrato(mensaje.value())
                
                # Procesar con la saga
                with app.app_context():
                    oir_mensaje(evento_dominio)
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("SAGA: Evento de contrato procesado y confirmado")
                
            except Exception as e:
                logger.error(f"SAGA: Error procesando evento de contrato: {e}")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"SAGA: Error en consumidor de contratos: {e}")
    finally:
        if cliente:
            cliente.close()


def _convertir_evento_influencer(evento_pulsar):
    """
    Convierte un evento de Pulsar a un evento de dominio InfluencerRegistrado.
    """
    logger.info(f"SAGA: Convirtiendo evento de influencer - {type(evento_pulsar)}")
    
    try:
        data = evento_pulsar.data
        
        # Crear evento de dominio compatible
        evento_dominio = InfluencerRegistrado(
            influencer_id=str(data.id_influencer),
            nombre=str(data.nombre),
            email=str(data.email),
            categorias=list(data.categorias) if data.categorias else [],
            plataformas=[],  # Valor por defecto
            fecha_registro=datetime.fromtimestamp(data.fecha_registro / 1000.0) if data.fecha_registro else datetime.utcnow()
        )
        
        logger.info(f"SAGA: Evento de influencer convertido - ID: {evento_dominio.influencer_id}")
        return evento_dominio
        
    except Exception as e:
        logger.error(f"SAGA: Error convirtiendo evento de influencer: {e}")
        raise


def _convertir_evento_campana(evento_pulsar):
    """
    Convierte un evento de Pulsar a un evento de dominio CampanaCreada.
    """
    logger.info(f"SAGA: Convirtiendo evento de campaña - {type(evento_pulsar)}")
    
    try:
        data = evento_pulsar.data
        
        # Crear evento de dominio compatible
        evento_dominio = CampanaCreada(
            campana_id=str(data.campana_id),
            nombre=str(data.nombre),
            descripcion=str(data.descripcion),
            tipo_comision=str(data.tipo_comision),
            valor_comision=float(data.valor_comision),
            moneda=str(data.moneda) if data.moneda else "USD",
            categorias_objetivo=list(data.categorias_objetivo) if data.categorias_objetivo else [],
            fecha_inicio=datetime.fromisoformat(str(data.fecha_inicio).replace('Z', '+00:00')) if data.fecha_inicio else datetime.utcnow(),
            fecha_fin=datetime.fromisoformat(str(data.fecha_fin).replace('Z', '+00:00')) if data.fecha_fin else None,
            influencer_id=str(data.influencer_id) if data.influencer_id else None,
            influencer_nombre=str(data.influencer_nombre) if data.influencer_nombre else None,
            influencer_email=str(data.influencer_email) if data.influencer_email else None
        )
        
        logger.info(f"SAGA: Evento de campaña convertido - ID: {evento_dominio.campana_id}")
        return evento_dominio
        
    except Exception as e:
        logger.error(f"SAGA: Error convirtiendo evento de campaña: {e}")
        raise


def _convertir_evento_contrato(evento_pulsar):
    """
    Convierte un evento de Pulsar a un evento de dominio ContratoCreado.
    """
    logger.info(f"SAGA: Convirtiendo evento de contrato - {type(evento_pulsar)}")
    
    try:
        data = evento_pulsar.data
        
        # Crear evento de dominio compatible
        evento_dominio = ContratoCreado(
            contrato_id=str(data.id_contrato),
            influencer_id=str(data.id_influencer),
            campana_id=str(data.id_campana),
            monto_total=float(data.monto_total),
            moneda=str(data.moneda) if data.moneda else "USD",
            fecha_inicio=datetime.utcnow(),  # Valor por defecto
            fecha_fin=None,  # Valor por defecto
            tipo_contrato=str(data.tipo_contrato),
            fecha_creacion=datetime.fromisoformat(str(data.fecha_creacion).replace('Z', '+00:00')) if data.fecha_creacion else datetime.utcnow()
        )
        
        logger.info(f"SAGA: Evento de contrato convertido - ID: {evento_dominio.contrato_id}")
        return evento_dominio
        
    except Exception as e:
        logger.error(f"SAGA: Error convirtiendo evento de contrato: {e}")
        raise
