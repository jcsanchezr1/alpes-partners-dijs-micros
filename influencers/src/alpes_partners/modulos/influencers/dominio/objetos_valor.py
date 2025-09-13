from enum import Enum
from typing import List, Dict
from src.alpes_partners.seedwork.dominio.objetos_valor import ObjetoValor


class TipoInfluencer(Enum):
    """Tipos de influencers según su alcance."""
    NANO = "nano"           # 1K - 10K seguidores
    MICRO = "micro"         # 10K - 100K seguidores
    MACRO = "macro"         # 100K - 1M seguidores
    MEGA = "mega"           # 1M+ seguidores
    CELEBRITY = "celebrity" # Celebridades


class EstadoInfluencer(Enum):
    """Estados posibles de un influencer."""
    PENDIENTE = "pendiente"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
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


class CategoriaInfluencer(ObjetoValor):
    """Categorías de contenido que maneja el influencer."""
    
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
    
    def calcular_tipo_influencer(self) -> TipoInfluencer:
        """Calcula el tipo de influencer basado en seguidores."""
        if self.seguidores < 10000:
            return TipoInfluencer.NANO
        elif self.seguidores < 100000:
            return TipoInfluencer.MICRO
        elif self.seguidores < 1000000:
            return TipoInfluencer.MACRO
        elif self.seguidores < 10000000:
            return TipoInfluencer.MEGA
        else:
            return TipoInfluencer.CELEBRITY


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


class PerfilInfluencer(ObjetoValor):
    """Perfil completo del influencer."""
    
    def __init__(self, 
                 categorias: CategoriaInfluencer,
                 descripcion: str,
                 sitio_web: str = "",
                 biografia: str = ""):
        self.categorias = categorias
        self.descripcion = descripcion.strip()
        self.sitio_web = sitio_web.strip()
        self.biografia = biografia.strip()
        
        if not self.descripcion:
            raise ValueError("La descripción es requerida")


class MetricasInfluencer(ObjetoValor):
    """Métricas de rendimiento del influencer."""
    
    def __init__(self, 
                 campanas_completadas: int = 0,
                 engagement_promedio: float = 0.0,
                 cpm_promedio: float = 0.0,
                 ingresos_generados: float = 0.0):
        if campanas_completadas < 0:
            raise ValueError("Las campanas completadas no pueden ser negativas")
        if engagement_promedio < 0:
            raise ValueError("El engagement promedio no puede ser negativo")
        if cpm_promedio < 0:
            raise ValueError("El CPM promedio no puede ser negativo")
        if ingresos_generados < 0:
            raise ValueError("Los ingresos generados no pueden ser negativos")
        
        self.campanas_completadas = campanas_completadas
        self.engagement_promedio = engagement_promedio
        self.cpm_promedio = cpm_promedio
        self.ingresos_generados = ingresos_generados
    
    def calcular_valor_por_mil(self) -> float:
        """Calcula el valor por mil impresiones."""
        return self.cpm_promedio if self.cpm_promedio > 0 else 0.0
