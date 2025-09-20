"""
Esquemas de comandos de integración para la saga.
"""

from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class CrearCampanaPayload(Record):
    """Payload del comando de crear campaña."""
    fecha_creacion = String()
    fecha_actualizacion = String()
    id = String()
    nombre = String()
    descripcion = String()
    tipo_comision = String()
    valor_comision = Float()
    moneda = String()
    fecha_inicio = String()
    fecha_fin = String(default=None, required=False)
    titulo_material = String()
    descripcion_material = String()
    categorias_objetivo = Array(String())
    tipos_afiliado_permitidos = Array(String())
    paises_permitidos = Array(String())
    enlaces_material = Array(String())
    imagenes_material = Array(String())
    banners_material = Array(String())
    metricas_minimas = String()  # JSON como string
    auto_activar = Boolean()
    influencer_origen_id = String(default=None, required=False)
    categoria_origen = String(default=None, required=False)
    influencer_origen_nombre = String(default=None, required=False)
    influencer_origen_email = String(default=None, required=False)


class ComandoCrearCampana(EventoIntegracion):
    """Comando de integración para crear campaña."""
    data = CrearCampanaPayload()


class CrearContratoPayload(Record):
    """Payload del comando de crear contrato."""
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
    fecha_fin = String(default=None, required=False)
    entregables = String(default=None, required=False)
    tipo_contrato = String()


class ComandoCrearContrato(EventoIntegracion):
    """Comando de integración para crear contrato."""
    data = CrearContratoPayload()