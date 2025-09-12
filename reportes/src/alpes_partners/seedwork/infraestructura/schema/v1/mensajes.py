"""Mensajes base para el seedwork."""

from pulsar.schema import Record, String, Integer, Float, Boolean
from typing import Optional


class MensajeBase(Record):
    """Mensaje base para todos los esquemas."""
    
    id = String()
    timestamp = String()
    version = String()


class ComandoBase(MensajeBase):
    """Comando base."""
    
    tipo_comando = String()
    origen = String()


class EventoBase(MensajeBase):
    """Evento base."""
    
    tipo_evento = String()
    agregado_id = String()
    agregado_tipo = String()
