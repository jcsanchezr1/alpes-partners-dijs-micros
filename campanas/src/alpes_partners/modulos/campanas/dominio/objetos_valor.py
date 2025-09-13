from enum import Enum
from datetime import datetime
from typing import List, Optional
from alpes_partners.seedwork.dominio.objetos_valor import ObjetoValor, Dinero


class TipoComision(Enum):
    """Tipos de comisión según el texto del negocio."""
    CPA = "cpa"  # Cost Per Action (por acción/conversión)
    CPL = "cpl"  # Cost Per Lead (por lead generado)
    CPC = "cpc"  # Cost Per Click (por clic)


class EstadoCampana(Enum):
    """Estados posibles de una campana."""
    BORRADOR = "borrador"
    ACTIVA = "activa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class TerminosComision(ObjetoValor):
    """Términos de comisión para una campana."""
    
    def __init__(self, 
                 tipo: TipoComision,
                 valor: Dinero,
                 descripcion: str = ""):
        self.tipo = tipo
        self.valor = valor
        self.descripcion = descripcion.strip()
        
        if self.valor.cantidad <= 0:
            raise ValueError("El valor de la comisión debe ser mayor a 0")


class PeriodoCampana(ObjetoValor):
    """Período de vigencia de una campana."""
    
    def __init__(self, 
                 fecha_inicio: datetime,
                 fecha_fin: Optional[datetime] = None):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
    
    def esta_activa(self, fecha_actual: Optional[datetime] = None) -> bool:
        """Verifica si la campana está en período activo."""
        if fecha_actual is None:
            fecha_actual = datetime.utcnow()
        
        if fecha_actual < self.fecha_inicio:
            return False
        
        if self.fecha_fin and fecha_actual > self.fecha_fin:
            return False
        
        return True


class MaterialPromocional(ObjetoValor):
    """Material promocional de la campana."""
    
    def __init__(self, 
                 titulo: str,
                 descripcion: str,
                 enlaces: List[str] = None,
                 imagenes: List[str] = None,
                 banners: List[str] = None):
        self.titulo = titulo.strip()
        self.descripcion = descripcion.strip()
        self.enlaces = enlaces or []
        self.imagenes = imagenes or []
        self.banners = banners or []
        
        if not self.titulo:
            raise ValueError("El título del material promocional es requerido")
        
        if not self.descripcion:
            raise ValueError("La descripción del material promocional es requerida")


class CriteriosAfiliado(ObjetoValor):
    """Criterios para seleccionar afiliados compatibles."""
    
    def __init__(self, 
                 tipos_permitidos: List[str] = None,
                 categorias_requeridas: List[str] = None,
                 paises_permitidos: List[str] = None,
                 metricas_minimas: dict = None):
        self.tipos_permitidos = tipos_permitidos or []
        self.categorias_requeridas = categorias_requeridas or []
        self.paises_permitidos = paises_permitidos or []
        self.metricas_minimas = metricas_minimas or {}


class MetricasCampana(ObjetoValor):
    """Métricas de rendimiento de la campana."""
    
    def __init__(self, 
                 afiliados_asignados: int = 0,
                 clics_totales: int = 0,
                 conversiones_totales: int = 0,
                 inversion_total: float = 0.0,
                 ingresos_generados: float = 0.0):
        self.afiliados_asignados = max(0, afiliados_asignados)
        self.clics_totales = max(0, clics_totales)
        self.conversiones_totales = max(0, conversiones_totales)
        self.inversion_total = max(0.0, inversion_total)
        self.ingresos_generados = max(0.0, ingresos_generados)
    
    def calcular_roi(self) -> float:
        """Calcula el ROI de la campana."""
        if self.inversion_total == 0:
            return 0.0
        return ((self.ingresos_generados - self.inversion_total) / self.inversion_total) * 100
    
    def calcular_tasa_conversion(self) -> float:
        """Calcula la tasa de conversión."""
        if self.clics_totales == 0:
            return 0.0
        return (self.conversiones_totales / self.clics_totales) * 100
