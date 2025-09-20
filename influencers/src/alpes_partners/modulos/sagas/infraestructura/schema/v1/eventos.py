"""
Esquemas de eventos de integración para la saga.
"""

from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class CampanaEliminacionRequeridaPayload(Record):
    """Payload del evento de eliminación de campaña requerida."""
    campana_id = String(default=None, required=False)
    influencer_id = String(default=None, required=False)
    razon = String(default=None, required=False)
    fecha_solicitud = String(default=None, required=False)


class EventoCampanaEliminacionRequerida(EventoIntegracion):
    """Evento de integración para solicitar eliminación de campaña."""
    data = CampanaEliminacionRequeridaPayload()
