from abc import ABC, abstractmethod
from typing import List, Optional
from ....seedwork.dominio.repositorios import Repositorio
from .entidades import SagaLog


class RepositorioSagaLog(Repositorio, ABC):
    """Repositorio para el log de sagas."""
    
    @abstractmethod
    def agregar(self, saga_log: SagaLog):
        """Agregar una entrada al log de saga."""
        ...
    
    @abstractmethod
    def obtener_por_correlacion(self, id_correlacion: str) -> List[SagaLog]:
        """Obtener todas las entradas de una saga por ID de correlación."""
        ...
    
    @abstractmethod
    def obtener_por_id(self, id_entrada: str) -> Optional[SagaLog]:
        """Obtener una entrada específica del log."""
        ...
    
    @abstractmethod
    def actualizar(self, saga_log: SagaLog):
        """Actualizar una entrada del log."""
        ...
