import logging
import time
import pulsar
import _pulsar
import uuid
from datetime import datetime
from pulsar.schema import AvroSchema
from alpes_partners.config.app import crear_app_minima
from alpes_partners.seedwork.infraestructura import utils
from alpes_partners.modulos.contratos.aplicacion.comandos.crear_contrato import CrearContrato, ejecutar_comando_crear_contrato
from alpes_partners.modulos.contratos.infraestructura.schema.v1.comandos import ComandoCrearContrato

logger = logging.getLogger(__name__)
app = crear_app_minima()

def suscribirse_a_comandos_contratos():
    """
    Suscribirse a comandos de contratos desde la saga.
    """
    cliente = None
    try:
        logger.info("CONTRATOS COMANDOS: Conectando a Pulsar para comandos...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'comandos-contratos-v2',
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='contratos-sub-comandos-v2',
            schema=AvroSchema(ComandoCrearContrato)
        )
        logger.info("CONTRATOS COMANDOS: Suscrito a comandos de contratos")
        logger.info("CONTRATOS COMANDOS: Esperando comandos...")

        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"CONTRATOS COMANDOS: Comando recibido - {mensaje.value()}")
                _procesar_comando_crear_contrato(mensaje.value())
                consumidor.acknowledge(mensaje)
                logger.info("CONTRATOS COMANDOS: Comando procesado y confirmado")
            except Exception as e:
                logger.error(f"CONTRATOS COMANDOS: Error procesando comando: {e}")
                import traceback
                logger.error(f"CONTRATOS COMANDOS: Traceback: {traceback.format_exc()}")
                time.sleep(5)
    except Exception as e:
        logger.error(f"CONTRATOS COMANDOS: Error en consumidor de comandos: {e}")
    finally:
        if cliente:
            cliente.close()

def _procesar_comando_crear_contrato(comando_integracion):
    """
    Procesa un comando de crear contrato desde la saga.
    """
    with app.app_context():
        try:
            logger.info("CONTRATOS COMANDOS: Procesando comando CrearContrato")
            data = comando_integracion.data

            comando = CrearContrato(
                fecha_creacion=data.fecha_creacion if hasattr(data, 'fecha_creacion') else datetime.utcnow().isoformat(),
                fecha_actualizacion=datetime.utcnow().isoformat(),
                id=str(uuid.uuid4()),
                influencer_id=data.influencer_id,
                influencer_nombre=data.influencer_nombre,
                influencer_email=data.influencer_email,
                campana_id=data.campana_id,
                campana_nombre=data.campana_nombre,
                categorias=data.categorias,
                descripcion=data.descripcion,
                monto_base=data.monto_base,
                moneda=data.moneda,
                fecha_inicio=data.fecha_inicio,
                fecha_fin=data.fecha_fin,
                entregables=data.entregables,
                tipo_contrato=data.tipo_contrato
            )
            ejecutar_comando_crear_contrato(comando)
            logger.info(f"CONTRATOS COMANDOS: Contrato {comando.id} creado desde comando de saga")
        except Exception as e:
            logger.error(f"CONTRATOS COMANDOS: Error al procesar comando CrearContrato: {e}")
            import traceback
            logger.error(f"CONTRATOS COMANDOS: Traceback: {traceback.format_exc()}")
