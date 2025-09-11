"""Modelos SQLAlchemy para reportes."""

from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class EstadoReporteEnum(enum.Enum):
    """Enum para estados de reporte en la base de datos."""
    ACTIVO = "activo"
    CANCELADO = "cancelado"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"


class TipoReporteEnum(enum.Enum):
    """Enum para tipos de reporte en la base de datos."""
    CAMPANA = "campana"
    CONTRATO = "contrato"
    GENERAL = "general"


class Reportes(Base):
    """Modelo SQLAlchemy para la tabla de reportes."""
    
    __tablename__ = 'reportes'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo_reporte = Column(SQLEnum(TipoReporteEnum), nullable=False)
    estado = Column(SQLEnum(EstadoReporteEnum), nullable=False, default=EstadoReporteEnum.ACTIVO)
    
    # Datos del evento origen
    datos_origen = Column(JSON, nullable=False)
    origen_evento = Column(String(100), nullable=False)
    
    # Metadatos
    metadatos = Column(JSON, nullable=True)
    
    # Configuración
    configuracion = Column(JSON, nullable=True)
    
    # Fechas
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Versión para control de concurrencia optimista
    version = Column(Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f"<Reporte(id='{self.id}', nombre='{self.nombre}', estado='{self.estado}')>"
