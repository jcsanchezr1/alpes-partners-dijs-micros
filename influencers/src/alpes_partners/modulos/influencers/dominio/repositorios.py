from abc import abstractmethod
from typing import List, Optional
from ....seedwork.dominio.repositorios import Repositorio
from .entidades import Influencer
from .objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma


class RepositorioInfluencers(Repositorio[Influencer]):
    """Repositorio para influencers."""
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Influencer]:
        """Obtiene un influencer por su email."""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: EstadoInfluencer) -> List[Influencer]:
        """Obtiene influencers por estado."""
        pass
    
    @abstractmethod
    def obtener_por_tipo(self, tipo: TipoInfluencer) -> List[Influencer]:
        """Obtiene influencers por tipo."""
        pass
    
    @abstractmethod
    def obtener_por_categoria(self, categoria: str) -> List[Influencer]:
        """Obtiene influencers que manejan una categoría específica."""
        pass
    
    @abstractmethod
    def obtener_por_plataforma(self, plataforma: Plataforma) -> List[Influencer]:
        """Obtiene influencers que están en una plataforma específica."""
        pass
    
    @abstractmethod
    def buscar_por_nombre(self, nombre: str) -> List[Influencer]:
        """Busca influencers por nombre (búsqueda parcial)."""
        pass
    
    @abstractmethod
    def obtener_por_rango_seguidores(self, min_seguidores: int, max_seguidores: int) -> List[Influencer]:
        """Obtiene influencers dentro de un rango de seguidores."""
        pass
    
    @abstractmethod
    def obtener_por_engagement_minimo(self, engagement_minimo: float) -> List[Influencer]:
        """Obtiene influencers con engagement mínimo."""
        pass
    
    @abstractmethod
    def existe_email(self, email: str) -> bool:
        """Verifica si existe un influencer con el email dado."""
        pass
