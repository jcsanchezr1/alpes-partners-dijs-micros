from pulsar.schema import Record, String, Float
from alpes_partners.seedwork.infraestructura.schema.v1.comandos import ComandoIntegracion

class CrearContratoPayload(Record):
    """Payload para comando de crear contrato desde la saga."""
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()

class ComandoCrearContrato(ComandoIntegracion):
    """Comando de integración para crear contrato desde la saga."""
    data = CrearContratoPayload()
