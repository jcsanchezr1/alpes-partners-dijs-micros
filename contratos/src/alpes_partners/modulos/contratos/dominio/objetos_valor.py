from enum import Enum
from typing import List, Dict
from datetime import datetime, date
from src.alpes_partners.seedwork.dominio.objetos_valor import ObjetoValor
from ....seedwork.dominio.objetos_valor import Dinero


class TipoContrato(Enum):
    """Tipos de contratos según el alcance y duración."""
    PUNTUAL = "puntual"         # Contrato de una sola campaña
    TEMPORAL = "temporal"       # Contrato por período específico
    EXCLUSIVO = "exclusivo"     # Contrato de exclusividad
    COLABORACION = "colaboracion" # Contrato de colaboración continua


class EstadoContrato(Enum):
    """Estados posibles de un contrato."""
    BORRADOR = "borrador"
    PENDIENTE = "pendiente"
    ACTIVO = "activo"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    SUSPENDIDO = "suspendido"


class Plataforma(Enum):
    """Plataformas de redes sociales."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"


class Genero(Enum):
    """Géneros demográficos."""
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    NO_BINARIO = "no_binario"
    OTRO = "otro"


class RangoEdad(Enum):
    """Rangos de edad para demografía."""
    EDAD_13_17 = "13-17"
    EDAD_18_24 = "18-24"
    EDAD_25_34 = "25-34"
    EDAD_35_44 = "35-44"
    EDAD_45_54 = "45-54"
    EDAD_55_PLUS = "55+"


class CategoriaContrato(ObjetoValor):
    """Categorías de contenido incluidas en el contrato."""
    
    def __init__(self, categorias: List[str]):
        if not categorias:
            raise ValueError("Debe tener al menos una categoría")
        self.categorias = [cat.lower().strip() for cat in categorias]


class DatosAudiencia(ObjetoValor):
    """Datos de audiencia del influencer en una plataforma."""
    
    def __init__(self, 
                 plataforma: Plataforma,
                 seguidores: int,
                 engagement_rate: float,
                 alcance_promedio: int = 0):
        if seguidores < 0:
            raise ValueError("El número de seguidores no puede ser negativo")
        if not (0 <= engagement_rate <= 100):
            raise ValueError("El engagement rate debe estar entre 0 y 100")
        if alcance_promedio < 0:
            raise ValueError("El alcance promedio no puede ser negativo")
        
        self.plataforma = plataforma
        self.seguidores = seguidores
        self.engagement_rate = engagement_rate
        self.alcance_promedio = alcance_promedio
    
    def calcular_tipo_influencer(self) -> TipoContrato:
        """Calcula el tipo de influencer basado en seguidores."""
        # Para contratos, el tipo se basa en el alcance esperado
        if self.seguidores < 10000:
            return TipoContrato.PUNTUAL
        elif self.seguidores < 100000:
            return TipoContrato.TEMPORAL
        elif self.seguidores < 1000000:
            return TipoContrato.COLABORACION
        else:
            return TipoContrato.EXCLUSIVO


class Demografia(ObjetoValor):
    """Demografía de la audiencia del influencer."""
    
    def __init__(self, 
                 distribucion_genero: Dict[Genero, float],
                 distribucion_edad: Dict[RangoEdad, float],
                 paises_principales: List[str]):
        # Validar que las distribuciones sumen aproximadamente 100%
        if abs(sum(distribucion_genero.values()) - 100.0) > 1.0:
            raise ValueError("La distribución de género debe sumar 100%")
        if abs(sum(distribucion_edad.values()) - 100.0) > 1.0:
            raise ValueError("La distribución de edad debe sumar 100%")
        
        self.distribucion_genero = distribucion_genero
        self.distribucion_edad = distribucion_edad
        self.paises_principales = paises_principales


class TerminosContrato(ObjetoValor):
    """Términos y condiciones del contrato."""
    
    def __init__(self, 
                 categorias: CategoriaContrato,
                 descripcion: str,
                 entregables: str = "",
                 condiciones_especiales: str = ""):
        self.categorias = categorias
        self.descripcion = descripcion.strip()
        self.entregables = entregables.strip()
        self.condiciones_especiales = condiciones_especiales.strip()
        
        if not self.descripcion:
            raise ValueError("La descripción del contrato es requerida")


class MetricasContrato(ObjetoValor):
    """Métricas de rendimiento del contrato."""
    
    def __init__(self, 
                 entregables_completados: int = 0,
                 engagement_alcanzado: float = 0.0,
                 costo_total: float = 0.0,
                 roi_obtenido: float = 0.0):
        if entregables_completados < 0:
            raise ValueError("Los entregables completados no pueden ser negativos")
        if engagement_alcanzado < 0:
            raise ValueError("El engagement alcanzado no puede ser negativo")
        if costo_total < 0:
            raise ValueError("El costo total no puede ser negativo")
        if roi_obtenido < 0:
            raise ValueError("El ROI obtenido no puede ser negativo")
        
        self.entregables_completados = entregables_completados
        self.engagement_alcanzado = engagement_alcanzado
        self.costo_total = costo_total
        self.roi_obtenido = roi_obtenido
    
    def calcular_costo_por_entregable(self) -> float:
        """Calcula el costo promedio por entregable."""
        return self.costo_total / self.entregables_completados if self.entregables_completados > 0 else 0.0


class PeriodoContrato(ObjetoValor):
    """Período de duración del contrato."""
    
    def __init__(self, 
                 fecha_inicio: datetime,
                 fecha_fin: datetime = None,
                 duracion_dias: int = None):
        if fecha_fin and fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.duracion_dias = duracion_dias
        
        # Si no se especifica fecha fin pero sí duración, calcular fecha fin
        if not fecha_fin and duracion_dias:
            from datetime import timedelta
            self.fecha_fin = fecha_inicio + timedelta(days=duracion_dias)
    
    def esta_vigente(self) -> bool:
        """Verifica si el contrato está vigente en la fecha actual."""
        ahora = datetime.now()
        if self.fecha_fin:
            return self.fecha_inicio <= ahora <= self.fecha_fin
        return ahora >= self.fecha_inicio


class CompensacionContrato(ObjetoValor):
    """Compensación económica del contrato."""
    
    def __init__(self, 
                 monto_base: Dinero,
                 tipo_compensacion: str = "fijo",  # fijo, por_entregable, por_resultado
                 bonificaciones: Dict[str, float] = None):
        self.monto_base = monto_base
        self.tipo_compensacion = tipo_compensacion
        self.bonificaciones = bonificaciones or {}
    
    def calcular_total_con_bonificaciones(self) -> float:
        """Calcula el total incluyendo bonificaciones."""
        total = self.monto_base.cantidad
        for concepto, monto in self.bonificaciones.items():
            total += monto
        return total


class InfluencerContrato(ObjetoValor):
    """Información del influencer asociado al contrato."""
    
    def __init__(self, 
                 influencer_id: str,
                 nombre: str,
                 email: str,
                 plataformas_principales: List[str]):
        if not influencer_id or not nombre or not email:
            raise ValueError("ID, nombre y email del influencer son requeridos")
        
        self.influencer_id = influencer_id
        self.nombre = nombre.strip()
        self.email = email.strip()
        self.plataformas_principales = plataformas_principales or []


class CampanaContrato(ObjetoValor):
    """Información de la campaña asociada al contrato."""
    
    def __init__(self, 
                 campana_id: str,
                 nombre: str,
                 descripcion: str = ""):
        if not campana_id or not nombre:
            raise ValueError("ID y nombre de la campaña son requeridos")
        
        self.campana_id = campana_id
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
