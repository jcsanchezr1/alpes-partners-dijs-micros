import pulsar
from pulsar.schema import *
import logging
from alpes_partners.seedwork.infraestructura import utils

logger = logging.getLogger(__name__)


def unix_time_millis(dt):
    return int(dt.timestamp() * 1000)


class DespachadorContratos:
    """Despachador para enviar comandos al microservicio de contratos."""

    def publicar(self, evento, topico, schema=None):
        try:
            cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
            publicador = cliente.create_producer(
                topico,
                schema=schema
            )
            publicador.send(evento)
            logger.info(f"SAGA DESPACHADOR: Comando enviado a {topico}")
            cliente.close()
        except Exception as e:
            logger.error(f"SAGA DESPACHADOR: Error enviando comando: {e}")
            raise

    def publicar_comando_crear_contrato(self, comando, topico='comandos-contratos-v2'):
        """Publica comando de crear contrato al microservicio de contratos."""
        try:
            from pulsar.schema import AvroSchema
            from ..infraestructura.schema.v1.comandos_contratos import ComandoCrearContrato, CrearContratoPayload
            import uuid
            from datetime import datetime
            
            # Crear payload del comando
            payload = CrearContratoPayload(
                influencer_id=comando.influencer_id,
                influencer_nombre=comando.influencer_nombre,
                influencer_email=comando.influencer_email,
                campana_id=comando.campana_id,
                campana_nombre=comando.campana_nombre,
                categorias=comando.categorias,
                descripcion=comando.descripcion,
                monto_base=comando.monto_base,
                moneda=comando.moneda,
                fecha_inicio=comando.fecha_inicio,
                fecha_fin=comando.fecha_fin,
                entregables=comando.entregables,
                tipo_contrato=comando.tipo_contrato
            )
            
            # Crear comando de integración
            comando_integracion = ComandoCrearContrato(
                id=str(uuid.uuid4()),
                time=datetime.utcnow(),
                ingestion=datetime.utcnow(),
                specversion="v1",
                type="CrearContratoRequerida",
                datacontenttype="AVRO",
                service_name="saga",
                data=payload
            )
            
            self.publicar(comando_integracion, topico, AvroSchema(ComandoCrearContrato))
            
        except Exception as e:
            logger.error(f"SAGA DESPACHADOR: Error publicando comando de crear contrato: {e}")
            raise


class DespachadorCampanas:
    """Despachador para enviar comandos al microservicio de campañas."""

    def publicar(self, evento, topico, schema=None):
        try:
            cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
            publicador = cliente.create_producer(
                topico,
                schema=schema
            )
            publicador.send(evento)
            logger.info(f"SAGA DESPACHADOR: Comando enviado a {topico}")
            cliente.close()
        except Exception as e:
            logger.error(f"SAGA DESPACHADOR: Error enviando comando: {e}")
            raise

    def publicar_comando_crear_campana(self, comando, topico='comandos-campanas'):
        """Publica comando de crear campaña al microservicio de campañas."""
        try:
            from pulsar.schema import AvroSchema
            from ..infraestructura.schema.v1.comandos import ComandoCrearCampana, CrearCampanaPayload
            import uuid
            from datetime import datetime
            import json
            
            # Convertir metricas_minimas a string JSON
            metricas_minimas_str = json.dumps(comando.metricas_minimas) if comando.metricas_minimas else "{}"
            
            # Crear payload del comando
            payload = CrearCampanaPayload(
                fecha_creacion=comando.fecha_creacion,
                fecha_actualizacion=comando.fecha_actualizacion,
                id=comando.id,
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                tipo_comision=comando.tipo_comision,
                valor_comision=comando.valor_comision,
                moneda=comando.moneda,
                fecha_inicio=comando.fecha_inicio,
                fecha_fin=comando.fecha_fin,
                titulo_material=comando.titulo_material,
                descripcion_material=comando.descripcion_material,
                categorias_objetivo=comando.categorias_objetivo,
                tipos_afiliado_permitidos=comando.tipos_afiliado_permitidos,
                paises_permitidos=comando.paises_permitidos,
                enlaces_material=comando.enlaces_material,
                imagenes_material=comando.imagenes_material,
                banners_material=comando.banners_material,
                metricas_minimas=metricas_minimas_str,
                auto_activar=comando.auto_activar,
                influencer_origen_id=comando.influencer_origen_id,
                categoria_origen=comando.categoria_origen,
                influencer_origen_nombre=comando.influencer_origen_nombre,
                influencer_origen_email=comando.influencer_origen_email
            )
            
            # Crear comando de integración
            comando_integracion = ComandoCrearCampana(
                id=str(uuid.uuid4()),
                time=datetime.utcnow(),
                ingestion=datetime.utcnow(),
                specversion="v1",
                type="CrearCampanaRequerida",
                datacontenttype="AVRO",
                service_name="saga",
                data=payload
            )
            
            self.publicar(comando_integracion, topico, AvroSchema(ComandoCrearCampana))
            
        except Exception as e:
            logger.error(f"SAGA DESPACHADOR: Error publicando comando de crear campaña: {e}")
            raise

    def publicar_evento_eliminacion_campana(self, evento, topico='eventos-campanas-eliminacion-v2'):
        """Publica evento de eliminación de campaña requerida."""
        try:
            from pulsar.schema import AvroSchema
            from ..infraestructura.schema.v1.eventos import EventoCampanaEliminacionRequerida, CampanaEliminacionRequeridaPayload
            import uuid
            from datetime import datetime
            
            # Crear payload del evento
            payload = CampanaEliminacionRequeridaPayload(
                campana_id=evento.campana_id,
                influencer_id=evento.influencer_id if evento.influencer_id else None,
                razon=evento.razon,
                fecha_solicitud=datetime.utcnow().isoformat()
            )
            
            # Crear evento de integración
            evento_integracion = EventoCampanaEliminacionRequerida(
                id=str(uuid.uuid4()),
                time=int(datetime.utcnow().timestamp() * 1000),
                ingestion=int(datetime.utcnow().timestamp() * 1000),
                specversion="1.0",
                type="CampanaEliminacionRequerida",
                datacontenttype="application/json",
                service_name="saga",
                data=payload
            )
            
            self.publicar(evento_integracion, topico, AvroSchema(EventoCampanaEliminacionRequerida))
            
        except Exception as e:
            logger.error(f"SAGA DESPACHADOR: Error publicando evento de eliminación: {e}")
            raise
