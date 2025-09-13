from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any
import json
import redis.asyncio as redis
from ..dominio.eventos import EventoDominio


class DespachadorEventos(ABC):
    """Interfaz para despachador de eventos."""
    
    @abstractmethod
    async def despachar(self, evento: EventoDominio) -> None:
        """Despacha un evento."""
        pass


class PublicadorEventos(ABC):
    """Interfaz para publicador de eventos."""
    
    @abstractmethod
    async def publicar(self, topico: str, mensaje: Dict[str, Any]) -> None:
        """Publica un mensaje en un tópico."""
        pass


class ConsumidorEventos(ABC):
    """Interfaz para consumidor de eventos."""
    
    @abstractmethod
    async def suscribirse(self, topico: str, handler: Callable) -> None:
        """Se suscribe a un tópico."""
        pass


class PublicadorEventosRedis(PublicadorEventos):
    """Publicador de eventos usando Redis."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    async def publicar(self, topico: str, mensaje: Dict[str, Any]) -> None:
        """Publica un mensaje en Redis."""
        mensaje_json = json.dumps(mensaje, default=str)
        await self.redis_client.publish(topico, mensaje_json)


class ConsumidorEventosRedis(ConsumidorEventos):
    """Consumidor de eventos usando Redis."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.handlers: Dict[str, List[Callable]] = {}
    
    async def suscribirse(self, topico: str, handler: Callable) -> None:
        """Se suscribe a un tópico."""
        if topico not in self.handlers:
            self.handlers[topico] = []
        self.handlers[topico].append(handler)
    
    async def iniciar_consumo(self) -> None:
        """Inicia el consumo de mensajes."""
        pubsub = self.redis_client.pubsub()
        
        # Suscribirse a todos los tópicos
        for topico in self.handlers.keys():
            await pubsub.subscribe(topico)
        
        async for mensaje in pubsub.listen():
            if mensaje['type'] == 'message':
                topico = mensaje['channel'].decode('utf-8')
                datos = json.loads(mensaje['data'].decode('utf-8'))
                
                # Ejecutar handlers
                if topico in self.handlers:
                    for handler in self.handlers[topico]:
                        await handler(datos)


class DespachadorEventosRedis(DespachadorEventos):
    """Despachador de eventos usando Redis."""
    
    def __init__(self, publicador: PublicadorEventos):
        self.publicador = publicador
    
    async def despachar(self, evento: EventoDominio) -> None:
        """Despacha un evento a Redis."""
        topico = f"{evento.__class__.__module__.split('.')[-2]}.{evento.__class__.__name__}"
        await self.publicador.publicar(topico, evento.to_dict())
