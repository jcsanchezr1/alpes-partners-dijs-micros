from abc import abstractmethod
from typing import List, Optional

from alpes_partners.seedwork.dominio.repositorios import Repositorio
from .entidades import Reporte
from .objetos_valor import EstadoReporte, TipoReporte


class RepositorioReportes(Repositorio[Reporte]):
    """Interfaz del repositorio de reportes."""
    
    @abstractmethod
    async def obtener_por_estado(self, estado: EstadoReporte) -> List[Reporte]:
        """Obtiene reportes por estado."""
        pass
    
    @abstractmethod
    async def obtener_por_tipo(self, tipo: TipoReporte) -> List[Reporte]:
        """Obtiene reportes por tipo."""
        pass
    
    @abstractmethod
    async def obtener_por_origen_evento(self, origen_evento: str) -> List[Reporte]:
        """Obtiene reportes por origen del evento."""
        pass
    
    @abstractmethod
    async def buscar_por_nombre(self, nombre: str) -> List[Reporte]:
        """Busca reportes por nombre (búsqueda parcial)."""
        pass
