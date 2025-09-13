from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class InfluencerRegistradoPayload(Record):
    id_influencer = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    fecha_registro = Long()


class EventoInfluencerRegistrado(EventoIntegracion):
    data = InfluencerRegistradoPayload()
