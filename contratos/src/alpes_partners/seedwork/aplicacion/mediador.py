from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from .comandos import Comando
from .queries import Query, QueryResultado
from .handlers import ManejadorComando, ManejadorQuery


class Mediador(ABC):
    """Interfaz del mediador para comandos y queries."""
    
    @abstractmethod
    def enviar_comando(self, comando: Comando) -> None:
        """Envía un comando al manejador correspondiente."""
        pass
    
    @abstractmethod
    def enviar_query(self, query: Query) -> QueryResultado:
        """Envía una query al manejador correspondiente."""
        pass


class MediadorMemoria(Mediador):
    """Implementación en memoria del mediador."""
    
    def __init__(self):
        self._manejadores_comandos: Dict[Type[Comando], ManejadorComando] = {}
        self._manejadores_queries: Dict[Type[Query], ManejadorQuery] = {}
    
    def registrar_manejador_comando(self, tipo_comando: Type[Comando], manejador: ManejadorComando):
        """Registra un manejador para un tipo de comando."""
        self._manejadores_comandos[tipo_comando] = manejador
    
    def registrar_manejador_query(self, tipo_query: Type[Query], manejador: ManejadorQuery):
        """Registra un manejador para un tipo de query."""
        self._manejadores_queries[tipo_query] = manejador
    
    def enviar_comando(self, comando: Comando) -> None:
        """Envía un comando al manejador correspondiente."""
        tipo_comando = type(comando)
        if tipo_comando not in self._manejadores_comandos:
            raise ValueError(f"No hay manejador registrado para el comando {tipo_comando.__name__}")
        
        manejador = self._manejadores_comandos[tipo_comando]
        manejador.handle(comando)
    
    def enviar_query(self, query: Query) -> QueryResultado:
        """Envía una query al manejador correspondiente."""
        tipo_query = type(query)
        if tipo_query not in self._manejadores_queries:
            raise ValueError(f"No hay manejador registrado para la query {tipo_query.__name__}")
        
        manejador = self._manejadores_queries[tipo_query]
        return manejador.handle(query)
