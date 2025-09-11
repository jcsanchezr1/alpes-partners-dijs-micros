from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, validator
from src.alpes_partners.seedwork.aplicacion.dto import DTO
from ..dominio.objetos_valor import TipoContrato, EstadoContrato, Plataforma, Genero, RangoEdad

class CrearContratoDTO(DTO):
    """DTO para crear un contrato."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    influencer_id: str
    influencer_nombre: str
    influencer_email: EmailStr
    campana_id: str
    campana_nombre: str
    categorias: List[str]
    descripcion: str
    monto_base: float
    moneda: str = "USD"
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    entregables: Optional[str] = ""
    tipo_contrato: str = "puntual"
    
    @validator('influencer_nombre')
    def validar_influencer_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre del influencer es requerido')
        return v.strip()
    
    @validator('campana_nombre')
    def validar_campana_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de la campaña es requerido')
        return v.strip()
    
    @validator('categorias')
    def validar_categorias(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos una categoría')
        return v
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if not v or not v.strip():
            raise ValueError('La descripción del contrato es requerida')
        return v.strip()
    
    @validator('monto_base')
    def validar_monto_base(cls, v):
        if v <= 0:
            raise ValueError('El monto base debe ser mayor a 0')
        return v


class ContratoDTO(DTO):
    """DTO para representar un contrato."""
    id: str
    influencer_id: str
    influencer_nombre: str
    influencer_email: str
    campana_id: str
    campana_nombre: str
    estado: EstadoContrato
    tipo_contrato: TipoContrato
    categorias: List[str]
    descripcion: str
    entregables: Optional[str] = ""
    monto_base: float
    moneda: str
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    fecha_creacion: str
    fecha_firma: Optional[str] = None
    fecha_finalizacion: Optional[str] = None
    
    # Métricas del contrato
    entregables_completados: int = 0
    engagement_alcanzado: float = 0.0
    costo_total: float = 0.0
    roi_obtenido: float = 0.0
