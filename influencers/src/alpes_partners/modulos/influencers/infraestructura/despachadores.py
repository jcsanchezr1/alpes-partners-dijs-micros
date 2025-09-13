import pulsar
from pulsar.schema import *

from alpes_partners.modulos.influencers.infraestructura.schema.v1.eventos import (
    EventoInfluencerRegistrado, InfluencerRegistradoPayload
)
from alpes_partners.seedwork.infraestructura import utils

import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


class DespachadorInfluencers:
    def _publicar_mensaje(self, mensaje, topico, schema):
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        publicador = cliente.create_producer(topico, schema=schema)
        publicador.send(mensaje)
        cliente.close()

    def publicar_evento_influencer_registrado(self, evento, topico='eventos-influencers'):
        """Publica evento cuando un influencer es registrado."""
        payload = InfluencerRegistradoPayload(
            id_influencer=str(evento.influencer_id), 
            nombre=str(evento.nombre), 
            email=str(evento.email), 
            categorias=evento.categorias,
            fecha_registro=int(unix_time_millis(evento.fecha_registro))
        )
        evento_integracion = EventoInfluencerRegistrado(
            id=str(evento.id),
            time=int(unix_time_millis(evento.fecha_registro)),
            ingestion=int(unix_time_millis(datetime.datetime.utcnow())),
            specversion="1.0",
            type="InfluencerRegistrado",
            datacontenttype="application/json",
            service_name="alpes-partners-influencers",
            data=payload
        )
        self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoInfluencerRegistrado))
