"""
Schema Avro para comandos de campanas.
Define los comandos que campanas recibe de otros microservicios.
"""

from pulsar.schema import Record, String, Float, Array, Boolean
from alpes_partners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class CrearCampanaPayload(Record):
    """Payload del comando CrearCampanaRequerida que campanas recibe."""
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