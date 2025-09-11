from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.comandos import ComandoIntegracion


class CrearContratoPayload(Record):
    influencer_id = String()
    influencer_nombre = String()
    influencer_email = String()
    campana_id = String()
    campana_nombre = String()
    categorias = Array(String())
    descripcion = String()
    monto_base = Float()
    moneda = String()
    fecha_inicio = String()
    fecha_fin = String()
    entregables = String()
    tipo_contrato = String()


class ComandoCrearContrato(ComandoIntegracion):
    data = CrearContratoPayload()
