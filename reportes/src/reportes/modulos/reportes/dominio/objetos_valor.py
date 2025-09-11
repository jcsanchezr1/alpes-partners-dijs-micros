from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from reportes.seedwork.dominio.objetos_valor import ObjetoValor


class EstadoReporte(Enum):
    """Estados posibles de un reporte."""
    ACTIVO = "activo"
    CANCELADO = "cancelado"  # Para manejo de compensación con patrón Saga
    PROCESANDO = "procesando"
    COMPLETADO = "completado"


class TipoReporte(Enum):
    """Tipos de reporte disponibles."""
    CAMPANA = "campana"
    CONTRATO = "contrato"  # TODO: Implementar cuando se tenga el evento de contrato
    GENERAL = "general"


class MetadatosReporte(ObjetoValor):
    """Metadatos adicionales del reporte."""
    
    def __init__(self, 
                 origen_evento: str,
                 version_esquema: str = "1.0",
                 datos_adicionales: Dict[str, Any] = None):
        self.origen_evento = origen_evento
        self.version_esquema = version_esquema
        self.datos_adicionales = datos_adicionales or {}


class ConfiguracionReporte(ObjetoValor):
    """Configuración específica del reporte."""
    
    def __init__(self,
                 incluir_metricas: bool = True,
                 formato_salida: str = "json",
                 notificar_completado: bool = False):
        self.incluir_metricas = incluir_metricas
        self.formato_salida = formato_salida
        self.notificar_completado = notificar_completado
