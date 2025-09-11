import pulsar
from pulsar.schema import *

from alpes_partners.modulos.contratos.infraestructura.schema.v1.eventos import (
    EventoContratoCreado, ContratoCreadoPayload
)
from alpes_partners.seedwork.infraestructura import utils

import datetime

def unix_time_millis(dt):
    """Convierte datetime a timestamp en milisegundos."""
    return int(dt.timestamp() * 1000)


class DespachadorContratos:
    def _publicar_mensaje(self, mensaje, topico, schema):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema=schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento_contrato_creado(self, evento, topico='eventos-contratos'):
        """Publica evento cuando un contrato es creado."""
        payload = ContratoCreadoPayload(
            id_contrato=str(evento.contrato_id), 
            id_influencer=str(evento.influencer_id),
            id_campana=str(evento.campana_id),
            monto_total=float(evento.monto_total),
            moneda=str(evento.moneda),
            tipo_contrato=str(evento.tipo_contrato),
            fecha_creacion=str(evento.fecha_creacion)
        )
        evento_integracion = EventoContratoCreado(
            id=str(evento.id),
            time=unix_time_millis(evento.fecha_creacion),
            ingestion=unix_time_millis(datetime.datetime.utcnow()),
            specversion="1.0",
            type="ContratoCreado",
            datacontenttype="application/json",
            service_name="alpes-partners-contratos",
            data=payload
        )
        self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoContratoCreado))
