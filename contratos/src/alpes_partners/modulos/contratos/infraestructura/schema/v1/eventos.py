from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class ContratoCreadoPayload(Record):
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()


class EventoContratoCreado(EventoIntegracion):
    data = ContratoCreadoPayload()


# Esquemas específicos para eventos de error
class ContratoErrorPayload(Record):
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()
    error = String()
    error_detalle = String()


class EventoContratoError(EventoIntegracion):
    data = ContratoErrorPayload()