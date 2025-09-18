from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.orm import Session
import json
import logging

from ....seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ..dominio.repositorios import RepositorioSagaLog
from ..dominio.entidades import SagaLog

# Usar la misma Base que los modelos de influencers para creación automática
from ...influencers.infraestructura.modelos import Base

# Importar db como en el tutorial
from ....seedwork.infraestructura.database import db

logger = logging.getLogger(__name__)


class SagaLogModelo(Base):
    """Modelo SQLAlchemy para el log de sagas."""
    __tablename__ = 'saga_logs'
    
    id = Column(String, primary_key=True)
    id_correlacion = Column(String, nullable=False, index=True)
    evento_tipo = Column(String, nullable=False)
    evento_datos = Column(Text, nullable=False)  # JSON serializado
    paso_index = Column(Integer, nullable=True)
    fecha_procesamiento = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class RepositorioSagaLogSQLAlchemy(RepositorioSagaLog):
    """Implementación SQLAlchemy del repositorio de saga log."""
    
    def __init__(self):
        # Sin parámetros, usa db.session directamente como en el tutorial
        pass
    
    def agregar(self, saga_log: SagaLog):
        """Agregar una entrada al log de saga."""
        logger.info(f"SAGA LOG: Agregando entrada - Correlación: {saga_log.id_correlacion}")
        
        saga_log_modelo = SagaLogModelo()
        saga_log_modelo.id = saga_log.id
        saga_log_modelo.id_correlacion = saga_log.id_correlacion
        saga_log_modelo.evento_tipo = saga_log.evento_tipo
        saga_log_modelo.evento_datos = json.dumps(saga_log.evento_datos)
        saga_log_modelo.paso_index = saga_log.paso_index
        saga_log_modelo.fecha_procesamiento = saga_log.fecha_procesamiento
        saga_log_modelo.fecha_creacion = saga_log.fecha_creacion
        saga_log_modelo.fecha_actualizacion = saga_log.fecha_actualizacion
        
        db.session.add(saga_log_modelo)
        db.session.flush()
        
        logger.info(f"SAGA LOG: Entrada agregada exitosamente - ID: {saga_log.id}")
    
    def obtener_por_correlacion(self, id_correlacion: str) -> List[SagaLog]:
        """Obtener todas las entradas de una saga por ID de correlación."""
        logger.info(f"SAGA LOG: Buscando entradas por correlación: {id_correlacion}")
        
        modelos = db.session.query(SagaLogModelo).filter(
            SagaLogModelo.id_correlacion == id_correlacion
        ).order_by(SagaLogModelo.fecha_procesamiento).all()
        
        entradas = []
        for modelo in modelos:
            entrada = SagaLog(
                id_correlacion=modelo.id_correlacion,
                evento_tipo=modelo.evento_tipo,
                evento_datos=json.loads(modelo.evento_datos),
                paso_index=modelo.paso_index,
                fecha_procesamiento=modelo.fecha_procesamiento
            )
            entrada.id = modelo.id
            entrada.fecha_creacion = modelo.fecha_creacion
            entrada.fecha_actualizacion = modelo.fecha_actualizacion
            entradas.append(entrada)
        
        logger.info(f"SAGA LOG: Encontradas {len(entradas)} entradas")
        return entradas
    
    def obtener_por_id(self, id_entrada: str) -> Optional[SagaLog]:
        """Obtener una entrada específica del log."""
        modelo = db.session.query(SagaLogModelo).filter(
            SagaLogModelo.id == id_entrada
        ).first()
        
        if not modelo:
            return None
        
        entrada = SagaLog(
            id_correlacion=modelo.id_correlacion,
            evento_tipo=modelo.evento_tipo,
            evento_datos=json.loads(modelo.evento_datos),
            paso_index=modelo.paso_index,
            fecha_procesamiento=modelo.fecha_procesamiento
        )
        entrada.id = modelo.id
        entrada.fecha_creacion = modelo.fecha_creacion
        entrada.fecha_actualizacion = modelo.fecha_actualizacion
        
        return entrada
    
    def actualizar(self, saga_log: SagaLog):
        """Actualizar una entrada del log."""
        modelo = db.session.query(SagaLogModelo).filter(
            SagaLogModelo.id == saga_log.id
        ).first()
        
        if modelo:
            modelo.fecha_actualizacion = saga_log.fecha_actualizacion
            db.session.flush()
    
    def eliminar(self, saga_log: SagaLog):
        """Eliminar una entrada del log."""
        logger.info(f"SAGA LOG: Eliminando entrada - ID: {saga_log.id}")
        
        modelo = db.session.query(SagaLogModelo).filter(
            SagaLogModelo.id == saga_log.id
        ).first()
        
        if modelo:
            db.session.delete(modelo)
            db.session.flush()
            logger.info(f"SAGA LOG: Entrada eliminada exitosamente - ID: {saga_log.id}")
        else:
            logger.warning(f"SAGA LOG: No se encontró entrada para eliminar - ID: {saga_log.id}")
    
    def obtener_todos(self) -> List[SagaLog]:
        """Obtener todas las entradas del log."""
        logger.info("SAGA LOG: Obteniendo todas las entradas")
        
        modelos = db.session.query(SagaLogModelo).order_by(
            SagaLogModelo.fecha_procesamiento.desc()
        ).all()
        
        entradas = []
        for modelo in modelos:
            entrada = SagaLog(
                id_correlacion=modelo.id_correlacion,
                evento_tipo=modelo.evento_tipo,
                evento_datos=json.loads(modelo.evento_datos),
                comando_tipo=modelo.comando_tipo,
                comando_datos=json.loads(modelo.comando_datos) if modelo.comando_datos else None,
                paso_index=modelo.paso_index,
                estado=modelo.estado,
                fecha_procesamiento=modelo.fecha_procesamiento
            )
            entrada.id = modelo.id
            entrada.fecha_creacion = modelo.fecha_creacion
            entrada.fecha_actualizacion = modelo.fecha_actualizacion
            entradas.append(entrada)
        
        logger.info(f"SAGA LOG: Encontradas {len(entradas)} entradas totales")
        return entradas