import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InfluencerModelo(Base):
    """Modelo SQLAlchemy para Influencer."""
    
    __tablename__ = "influencers"
    
    # Campos básicos
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefono = Column(String(50), nullable=True)
    estado = Column(String(50), nullable=False, default="pendiente")
    
    # Perfil
    categorias = Column(JSON, nullable=False)
    descripcion = Column(Text, nullable=False)
    biografia = Column(Text, nullable=True)
    sitio_web = Column(String(500), nullable=True)
    
    # Audiencia por plataforma (JSON con estructura: {plataforma: {seguidores, engagement, alcance}})
    audiencia_por_plataforma = Column(JSON, nullable=True, default={})
    
    # Demografia (JSON con estructura: {genero: {}, edad: {}, paises: []})
    demografia = Column(JSON, nullable=True)
    
    # Métricas
    campanas_completadas = Column(Integer, nullable=False, default=0)
    engagement_promedio = Column(Float, nullable=False, default=0.0)
    cpm_promedio = Column(Float, nullable=False, default=0.0)
    ingresos_generados = Column(Float, nullable=False, default=0.0)
    
    # Campos calculados para optimizar consultas
    total_seguidores = Column(Integer, nullable=False, default=0)
    tipo_principal = Column(String(50), nullable=True)  # nano, micro, macro, mega, celebrity
    plataformas_activas = Column(JSON, nullable=True, default=[])  # Lista de plataformas
    
    # Fechas
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_activacion = Column(DateTime, nullable=True)
    fecha_desactivacion = Column(DateTime, nullable=True)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Control de versión
    version = Column(String, nullable=False, default="1")
    
    def __repr__(self):
        return f"<InfluencerModelo(id={self.id}, nombre={self.nombre}, email={self.email})>"
