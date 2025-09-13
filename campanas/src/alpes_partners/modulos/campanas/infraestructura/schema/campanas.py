"""
Schema de base de datos para campanas.
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum

Base = declarative_base()

class EstadoCampanaEnum(enum.Enum):
    """Estados de campana para la base de datos."""
    BORRADOR = "borrador"
    ACTIVA = "activa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class TipoComisionEnum(enum.Enum):
    """Tipos de comisión para la base de datos."""
    CPA = "cpa"  # Cost Per Action
    CPL = "cpl"  # Cost Per Lead
    CPC = "cpc"  # Cost Per Click


class Campanas(Base):
    """Tabla de campanas."""
    
    __tablename__ = 'campanas'
    
    # Campos básicos
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=False)
    
    # Términos de comisión
    tipo_comision = Column(SQLEnum(TipoComisionEnum), nullable=False)
    valor_comision = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False, default='USD')
    descripcion_comision = Column(Text, nullable=True)
    
    # Período de campana
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    
    # Estado y fechas de control
    estado = Column(SQLEnum(EstadoCampanaEnum), nullable=False, default=EstadoCampanaEnum.BORRADOR)
    fecha_activacion = Column(DateTime(timezone=True), nullable=True)
    fecha_pausa = Column(DateTime(timezone=True), nullable=True)
    
    # Material promocional (JSON)
    material_promocional = Column(JSON, nullable=False, default=dict)
    # Estructura: {
    #   "titulo": str,
    #   "descripcion": str,
    #   "enlaces": [str],
    #   "imagenes": [str],
    #   "banners": [str]
    # }
    
    # Criterios de afiliado (JSON)
    criterios_afiliado = Column(JSON, nullable=False, default=dict)
    # Estructura: {
    #   "tipos_permitidos": [str],
    #   "categorias_requeridas": [str],
    #   "paises_permitidos": [str],
    #   "metricas_minimas": dict
    # }
    
    # Métricas de campana (JSON)
    metricas = Column(JSON, nullable=False, default=dict)
    # Estructura: {
    #   "afiliados_asignados": int,
    #   "clics_totales": int,
    #   "conversiones_totales": int,
    #   "inversion_total": float,
    #   "ingresos_generados": float
    # }
    
    # Afiliados asignados (JSON array de IDs)
    afiliados_asignados = Column(JSON, nullable=False, default=list)
    
    # Campos para campanas automáticas
    influencer_origen_id = Column(String(50), nullable=True, index=True)
    categoria_origen = Column(String(100), nullable=True, index=True)
    es_automatica = Column(Boolean, nullable=False, default=False)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f"<Campana(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"


# Índices adicionales para optimizar consultas
from sqlalchemy import Index

# Índice compuesto para consultas por estado y fechas
Index('idx_campanas_estado_fechas', Campanas.estado, Campanas.fecha_inicio, Campanas.fecha_fin)

# Índice para consultas por categoría origen
Index('idx_campanas_categoria_origen', Campanas.categoria_origen)

# Índice para consultas por influencer origen
Index('idx_campanas_influencer_origen', Campanas.influencer_origen_id)

# Índice para consultas por tipo de comisión
Index('idx_campanas_tipo_comision', Campanas.tipo_comision)

# Índice para búsquedas de texto en nombre
Index('idx_campanas_nombre_text', Campanas.nombre)