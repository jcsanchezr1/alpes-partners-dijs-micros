"""
Esquemas de eventos de contratos para el BFF.
Basados en los esquemas del microservicio de contratos.
"""

from pulsar.schema import Record, String, Float, Long

class ContratoCreadoPayload(Record):
    """Payload del evento ContratoCreado."""
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()

class EventoIntegracion(Record):
    """Evento de integración base."""
    id = String()
    time = Long()
    ingestion = Long()
    specversion = String()
    type = String()
    datacontenttype = String()
    service_name = String()

class EventoContratoCreado(EventoIntegracion):
    """Evento de integración para contrato creado."""
    data = ContratoCreadoPayload()

class ContratoErrorPayload(Record):
    """Payload del evento ContratoError."""
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
    """Evento de integración para error de contrato."""
    data = ContratoErrorPayload()
