from abc import abstractmethod
from typing import List, Optional
from ....seedwork.dominio.repositorios import Repositorio
from .entidades import Contrato
from .objetos_valor import TipoContrato, EstadoContrato, Plataforma


class RepositorioContratos(Repositorio[Contrato]):
    """Repositorio para contratos."""
    
    @abstractmethod
    def obtener_por_influencer(self, influencer_id: str) -> List[Contrato]:
        """Obtiene contratos por ID de influencer."""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: EstadoContrato) -> List[Contrato]:
        """Obtiene contratos por estado."""
        pass
    
    @abstractmethod
    def obtener_por_tipo(self, tipo: TipoContrato) -> List[Contrato]:
        """Obtiene contratos por tipo."""
        pass
    
    @abstractmethod
    def obtener_por_campana(self, campana_id: str) -> List[Contrato]:
        """Obtiene contratos por ID de campaña."""
        pass
    
    @abstractmethod
    def obtener_por_categoria(self, categoria: str) -> List[Contrato]:
        """Obtiene contratos que incluyen una categoría específica."""
        pass
    
    @abstractmethod
    def obtener_vigentes(self) -> List[Contrato]:
        """Obtiene contratos vigentes."""
        pass
    
    @abstractmethod
    def obtener_por_rango_fechas(self, fecha_inicio: str, fecha_fin: str) -> List[Contrato]:
        """Obtiene contratos dentro de un rango de fechas."""
        pass
    
    @abstractmethod
    def obtener_por_monto_minimo(self, monto_minimo: float) -> List[Contrato]:
        """Obtiene contratos con monto mínimo."""
        pass
    
    @abstractmethod
    def existe_contrato_activo(self, influencer_email: str) -> bool:
        """Verifica si existe un contrato activo para el influencer (por email)."""
        pass
