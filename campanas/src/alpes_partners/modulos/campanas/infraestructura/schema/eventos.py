"""
Schema Avro para eventos de campanas.
Define los eventos que campanas publica para otros microservicios.
"""

from pulsar.schema import Record, String, Float, Array, Long
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class InfluencerRegistradoPayload(Record):
    """Payload del evento InfluencerRegistrado que campanas consume."""
    id_influencer = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    fecha_registro = Long()


class EventoInfluencerRegistrado(EventoIntegracion):
    """Evento de integración para influencer registrado."""
    data = InfluencerRegistradoPayload()


class CampanaCreadaPayload(Record):
    """Payload del evento CampanaCreada que campanas publica."""
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


class EventoCampanaCreada(EventoIntegracion):
    """Evento de integración para campaña creada."""
    data = CampanaCreadaPayload()


class CampanaEliminadaPayload(Record):
    """Payload del evento CampanaEliminada que campanas publica."""
    campana_id = String()
    influencer_id = String()
    razon = String()
    fecha_eliminacion = String()


class EventoCampanaEliminada(EventoIntegracion):
    """Evento de integración para campaña eliminada."""
    data = CampanaEliminadaPayload()


class CampanaEliminacionRequeridaPayload(Record):
    """Payload del evento de eliminación de campaña requerida que campanas consume."""
    campana_id = String()
    influencer_id = String()
    razon = String()
    fecha_solicitud = String()


class EventoCampanaEliminacionRequerida(EventoIntegracion):
    """Evento de integración para solicitar eliminación de campaña."""
    data = CampanaEliminacionRequeridaPayload()
