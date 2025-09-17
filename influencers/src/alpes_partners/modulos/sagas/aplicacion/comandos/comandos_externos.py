"""
Comandos que representan operaciones en otros microservicios.
Estos comandos se enviarán a través de eventos de integración o APIs.
"""

from dataclasses import dataclass
from typing import Optional, List
from .....seedwork.aplicacion.comandos import Comando


@dataclass
class RegistrarCampana(Comando):
    """Comando para registrar una nueva campaña (se enviará al microservicio campanas)."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo_comision: str
    valor_comision: float
    moneda: str
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    titulo_material: str = ""
    descripcion_material: str = ""
    categorias_objetivo: List[str] = None
    tipos_afiliado_permitidos: List[str] = None
    paises_permitidos: List[str] = None
    enlaces_material: List[str] = None
    imagenes_material: List[str] = None
    banners_material: List[str] = None
    metricas_minimas: dict = None
    auto_activar: bool = False
    influencer_origen_id: Optional[str] = None
    categoria_origen: Optional[str] = None
    influencer_origen_nombre: Optional[str] = None
    influencer_origen_email: Optional[str] = None


@dataclass
class CrearContrato(Comando):
    """Comando para crear un nuevo contrato (se enviará al microservicio contratos)."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    influencer_id: str
    influencer_nombre: str
    influencer_email: str
    campana_id: str
    campana_nombre: str
    categorias: List[str]
    descripcion: str
    monto_base: float
    moneda: str = "USD"
    fecha_inicio: str = None
    fecha_fin: Optional[str] = None
    entregables: Optional[str] = None
    tipo_contrato: str = "puntual"
