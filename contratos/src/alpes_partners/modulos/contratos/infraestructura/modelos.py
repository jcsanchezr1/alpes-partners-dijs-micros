import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ContratoModelo(Base):
    """Modelo SQLAlchemy para Contrato."""
    
    __tablename__ = "contratos"
    __table_args__ = (
        UniqueConstraint('influencer_id', 'campana_id', name='uq_contratos_influencer_campana'),
    )
    
    # Campos básicos del contrato
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Referencias a influencer y campaña
    influencer_id = Column(String(255), nullable=False)
    influencer_nombre = Column(String(255), nullable=False)
    influencer_email = Column(String(255), nullable=False)
    
    campana_id = Column(String(255), nullable=False)
    campana_nombre = Column(String(255), nullable=False)
    
    # Estado y tipo del contrato
    estado = Column(String(50), nullable=False, default="borrador")
    tipo_contrato = Column(String(50), nullable=False, default="puntual")
    
    # Términos del contrato
    categorias = Column(JSON, nullable=False)
    descripcion = Column(Text, nullable=False)
    entregables = Column(Text, nullable=True)
    condiciones_especiales = Column(Text, nullable=True)
    
    # Audiencia por plataforma (JSON con estructura: {plataforma: {seguidores, engagement, alcance}})
    audiencia_por_plataforma = Column(JSON, nullable=True, default={})
    
    # Demografia (JSON con estructura: {genero: {}, edad: {}, paises: []})
    demografia = Column(JSON, nullable=True)
    
    # Compensación económica
    monto_base = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False, default="USD")
    tipo_compensacion = Column(String(50), nullable=False, default="fijo")
    bonificaciones = Column(JSON, nullable=True, default={})
    
    # Métricas del contrato
    entregables_completados = Column(Integer, nullable=False, default=0)
    engagement_alcanzado = Column(Float, nullable=False, default=0.0)
    costo_total = Column(Float, nullable=False, default=0.0)
    roi_obtenido = Column(Float, nullable=False, default=0.0)
    
    # Período del contrato
    fecha_inicio_contrato = Column(DateTime, nullable=False)
    fecha_fin_contrato = Column(DateTime, nullable=True)
    duracion_dias = Column(Integer, nullable=True)
    
    # Campos calculados para optimizar consultas
    total_seguidores = Column(Integer, nullable=False, default=0)
    plataformas_principales = Column(JSON, nullable=True, default=[])  # Lista de plataformas del influencer
    
    # Fechas del contrato
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_firma = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Control de versión
    version = Column(String, nullable=False, default="1")
    
    def __repr__(self):
        return f"<ContratoModelo(id={self.id}, influencer={self.influencer_nombre}, campana={self.campana_nombre})>"
