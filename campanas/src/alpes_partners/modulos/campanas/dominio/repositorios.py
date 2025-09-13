"""
Repositorios para el dominio de campanas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Campana


class RepositorioCampanas(ABC):
    """Repositorio abstracto para campanas."""
    
    @abstractmethod
    def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
        """Obtiene una campana por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Campana]:
        """Obtiene una campana por su nombre."""
        pass
    
    @abstractmethod
    def obtener_activas(self) -> List[Campana]:
        """Obtiene todas las campanas activas."""
        pass
    
    @abstractmethod
    def obtener_por_categoria(self, categoria: str) -> List[Campana]:
        """Obtiene campanas que incluyan una categoría específica."""
        pass
    
    @abstractmethod
    def obtener_por_influencer_origen(self, influencer_id: str) -> List[Campana]:
        """Obtiene campanas creadas para un influencer específico."""
        pass
    
    @abstractmethod
    def obtener_todas(self, limite: int = 100, offset: int = 0) -> List[Campana]:
        """Obtiene todas las campanas con paginación."""
        pass
    
    @abstractmethod
    def agregar(self, campana: Campana) -> None:
        """Agrega una nueva campana."""
        pass
    
    @abstractmethod
    def actualizar(self, campana: Campana) -> None:
        """Actualiza una campana existente."""
        pass
    
    @abstractmethod
    def eliminar(self, campana_id: str) -> None:
        """Elimina una campana."""
        pass
    
    @abstractmethod
    def existe_con_nombre(self, nombre: str, excluir_id: Optional[str] = None) -> bool:
        """Verifica si existe una campana con el nombre dado."""
        pass
