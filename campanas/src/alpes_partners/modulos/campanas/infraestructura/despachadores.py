"""
Despachador de eventos para el módulo de campanas.
Publica eventos cuando se crean campanas para que otros microservicios puedan reaccionar.
"""

import pulsar
from pulsar.schema import AvroSchema
import datetime
import uuid
from alpes_partners.modulos.campanas.infraestructura.schema.eventos import (
    EventoCampanaCreada, CampanaCreadaPayload, EventoCampanaEliminada, CampanaEliminadaPayload
)
from alpes_partners.seedwork.infraestructura import utils

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    """Convierte datetime a unix timestamp en milisegundos."""
    return int(dt.timestamp() * 1000)


class DespachadorCampanas:
    """Despachador de eventos para campanas."""
    
    def _publicar_mensaje(self, mensaje, topico, schema):
        """Publica un mensaje en el tópico especificado."""
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema=schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento_campana_creada(self, evento, topico='eventos-campanas'):
        """Publica evento cuando una campaña es creada."""
        import logging
        logger = logging.getLogger(__name__)
        
        # DEBUG: Mostrar datos del evento antes de crear el payload
        logger.info(f"CAMPANAS DESPACHADOR: Datos del evento recibido:")
        logger.info(f"  - campana_id: {evento.campana_id}")
        logger.info(f"  - nombre: {evento.nombre}")
        logger.info(f"  - fecha_inicio: {evento.fecha_inicio} (tipo: {type(evento.fecha_inicio)})")
        logger.info(f"  - fecha_fin: {evento.fecha_fin} (tipo: {type(evento.fecha_fin)})")
        logger.info(f"  - influencer_id: {evento.influencer_id} (tipo: {type(evento.influencer_id)})")
        logger.info(f"  - influencer_nombre: {evento.influencer_nombre} (tipo: {type(evento.influencer_nombre)})")
        logger.info(f"  - influencer_email: {evento.influencer_email} (tipo: {type(evento.influencer_email)})")
        
        # Extraer datos del evento de dominio
        payload = CampanaCreadaPayload(
            campana_id=str(evento.campana_id),
            nombre=str(evento.nombre),
            descripcion=str(evento.descripcion),
            tipo_comision=str(evento.tipo_comision),
            valor_comision=float(evento.valor_comision),
            moneda=str(evento.moneda),
            categorias_objetivo=evento.categorias_objetivo or [],
            fecha_inicio=str(evento.fecha_inicio),
            fecha_fin=str(evento.fecha_fin) if evento.fecha_fin and evento.fecha_fin != 'None' else None,
            # Campos adicionales para crear contratos
            influencer_id=str(evento.influencer_id) if evento.influencer_id and evento.influencer_id != 'None' else None,
            influencer_nombre=str(evento.influencer_nombre) if evento.influencer_nombre and evento.influencer_nombre != 'None' else None,
            influencer_email=str(evento.influencer_email) if evento.influencer_email and evento.influencer_email != 'None' else None,
            monto_base=float(evento.valor_comision) if evento.valor_comision else 0.0,
            entregables="Promoción de campaña",
            tipo_contrato="puntual",
            fecha_creacion=str(evento.fecha_creacion)
        )
        
        # DEBUG: Mostrar datos del payload creado
        logger.info(f"CAMPANAS DESPACHADOR: Payload creado:")
        logger.info(f"  - influencer_id: {payload.influencer_id} (tipo: {type(payload.influencer_id)})")
        logger.info(f"  - influencer_nombre: {payload.influencer_nombre} (tipo: {type(payload.influencer_nombre)})")
        logger.info(f"  - influencer_email: {payload.influencer_email} (tipo: {type(payload.influencer_email)})")
        
        evento_integracion = EventoCampanaCreada(
            id=str(evento.id),
            time=unix_time_millis(evento.fecha_creacion),
            ingestion=unix_time_millis(datetime.datetime.utcnow()),
            specversion="1.0",
            type="CampanaCreada",
            datacontenttype="application/json",
            service_name="alpes-partners-campanas",
            data=payload
        )
        
        self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoCampanaCreada))
    
    def publicar_evento_campana_eliminada(self, campana_id: str, influencer_id: str, razon: str, topico='eventos-campanas-eliminacion'):
        """Publica evento cuando una campaña es eliminada."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"CAMPANAS DESPACHADOR: Publicando evento de eliminación de campaña")
        logger.info(f"  - campana_id: {campana_id}")
        logger.info(f"  - influencer_id: {influencer_id}")
        logger.info(f"  - razon: {razon}")
        
        # Crear payload del evento de eliminación
        payload = CampanaEliminadaPayload(
            campana_id=str(campana_id),
            influencer_id=str(influencer_id),
            razon=str(razon),
            fecha_eliminacion=datetime.datetime.utcnow().isoformat()
        )
        
        # Crear evento de integración
        evento_integracion = EventoCampanaEliminada(
            id=str(uuid.uuid4()),
            time=unix_time_millis(datetime.datetime.utcnow()),
            ingestion=unix_time_millis(datetime.datetime.utcnow()),
            specversion="1.0",
            type="CampanaEliminada",
            datacontenttype="application/json",
            service_name="alpes-partners-campanas",
            data=payload
        )
        
        self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoCampanaEliminada))
