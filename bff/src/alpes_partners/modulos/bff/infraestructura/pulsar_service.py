"""
Servicio para enviar mensajes a Pulsar.
"""

import logging
import pulsar
from pulsar.schema import Record, String, Array, Long, AvroSchema
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CrearInfluencerPayload(Record):
    """Payload del evento CrearInfluencer."""
    id = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    descripcion = String(default=None, required=False)
    biografia = String(default=None, required=False)
    sitio_web = String(default=None, required=False)
    telefono = String(default=None, required=False)
    fecha_creacion = String()
    fecha_actualizacion = String()


class EventoCrearInfluencer(Record):
    """Evento de integración para crear influencer."""
    data = CrearInfluencerPayload()


class PulsarService:
    """Servicio para enviar mensajes a Pulsar."""
    
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.client = None
        self.producer = None
    
    def conectar(self):
        """Conecta al broker de Pulsar."""
        try:
            logger.info(f"Intentando conectar a Pulsar en: {self.broker_url}")
            self.client = pulsar.Client(f'pulsar://{self.broker_url}')
            self.producer = self.client.create_producer(
                'eventos-crear-influencer',
                schema=AvroSchema(EventoCrearInfluencer)
            )
            logger.info("Conectado exitosamente a Pulsar")
        except Exception as e:
            logger.error(f"Error conectando a Pulsar en {self.broker_url}: {e}")
            raise
    
    def enviar_evento_crear_influencer(
        self, 
        id_influencer: str, 
        nombre: str, 
        email: str, 
        categorias: List[str],
        descripcion: str = "",
        biografia: str = "",
        sitio_web: str = "",
        telefono: str = ""
    ):
        """Envía un evento de crear influencer."""
        try:
            if not self.producer:
                self.conectar()
            
            # Crear fechas en formato ISO
            fecha_actual = datetime.now().isoformat()
            
            # Crear payload del evento
            payload = CrearInfluencerPayload(
                id=id_influencer,
                nombre=nombre,
                email=email,
                categorias=categorias,
                descripcion=descripcion,
                biografia=biografia,
                sitio_web=sitio_web,
                telefono=telefono,
                fecha_creacion=fecha_actual,
                fecha_actualizacion=fecha_actual
            )
            
            # Crear evento de integración
            evento = EventoCrearInfluencer(data=payload)
            
            # Enviar mensaje
            self.producer.send(evento)
            logger.info(f"Evento de crear influencer enviado: {id_influencer}")
            
        except Exception as e:
            logger.error(f"Error enviando evento de crear influencer: {e}")
            raise
    
    def cerrar(self):
        """Cierra la conexión con Pulsar."""
        if self.producer:
            self.producer.close()
        if self.client:
            self.client.close()
        logger.info("Conexión con Pulsar cerrada")
