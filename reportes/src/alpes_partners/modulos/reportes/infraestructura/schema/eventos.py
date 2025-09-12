"""
Schema de eventos Pulsar para contratos - usado por reportes para consumir eventos.
"""

from pulsar.schema import Record, String, Float, Array, Long
from alpes_partners.seedwork.infraestructura.schema.v1.mensajes import EventoBase


class ContratoCreadoPayload(Record):
    """Payload del evento ContratoCreado para Pulsar."""
    
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()  


class EventoContratoCreado(EventoBase):
    """Evento de contrato creado para consumo en reportes."""
    
    data = ContratoCreadoPayload()
