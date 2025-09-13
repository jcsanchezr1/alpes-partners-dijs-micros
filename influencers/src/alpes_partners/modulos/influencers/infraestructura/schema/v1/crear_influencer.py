"""
Schema Avro para eventos de crear influencer.
"""

from typing import List
from pulsar.schema import Record, String, Array


class CrearInfluencerPayload(Record):
    """Payload del evento CrearInfluencer."""
    
    id = String()
    nombre = String()
    email = String()
    categorias = Array(String())  # Lista de categorías
    descripcion = String(default=None, required=False)
    biografia = String(default=None, required=False)
    sitio_web = String(default=None, required=False)
    telefono = String(default=None, required=False)
    fecha_creacion = String()  # ISO format datetime
    fecha_actualizacion = String()  # ISO format datetime


class EventoCrearInfluencer(Record):
    """Evento de integración para crear influencer."""
    
    data = CrearInfluencerPayload()
