"""
Schema Avro para eventos de video detectado.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pulsar.schema import Record, String, Long, Map, Union, Null
from ....dominio.eventos import VideoDetectado


class VideoDetectadoPayload(Record):
    """Payload del evento VideoDetectado."""
    
    video_id = String()
    influencer_id = String()
    plataforma = String()
    url_video = String()
    titulo = String()
    descripcion = Union([String(), Null()])
    duracion_segundos = Long()
    fecha_deteccion = String()  # ISO format datetime
    metadatos = Map(String())
    
    # Datos del influencer para creación automática
    influencer_nombre = Union([String(), Null()])
    influencer_email = Union([String(), Null()])
    influencer_categorias = Union([String(), Null()])  # JSON string
    influencer_descripcion = Union([String(), Null()])
    influencer_biografia = Union([String(), Null()])
    influencer_sitio_web = Union([String(), Null()])
    influencer_telefono = Union([String(), Null()])


class EventoVideoDetectado(Record):
    """Evento de integración para video detectado."""
    
    id = String()
    id_entidad = String()
    fecha_evento = String()
    version = String()
    data = VideoDetectadoPayload()
