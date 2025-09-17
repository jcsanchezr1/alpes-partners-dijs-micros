"""
Script para crear las tablas necesarias para el saga log.
Ejecutar este script una vez para inicializar la base de datos.
"""

from sqlalchemy import create_engine, text
from .repositorio_saga_log import Base, SagaLogModelo
import logging

logger = logging.getLogger(__name__)

def crear_tabla_saga_logs(database_url: str = None):
    """Crear la tabla saga_logs en la base de datos."""
    
    if not database_url:
        # Usar la configuración por defecto (ajustar según tu configuración)
        database_url = "sqlite:///saga_logs.db"
    
    try:
        logger.info(f"SAGA MIGRATION: Conectando a la base de datos: {database_url}")
        engine = create_engine(database_url)
        
        # Crear todas las tablas definidas en Base
        Base.metadata.create_all(engine)
        
        logger.info("SAGA MIGRATION: Tabla saga_logs creada exitosamente")
        
        # Verificar que la tabla fue creada
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='saga_logs'"))
            if result.fetchone():
                logger.info("SAGA MIGRATION: Verificación exitosa - tabla saga_logs existe")
            else:
                logger.warning("SAGA MIGRATION: La tabla saga_logs no fue encontrada después de la creación")
                
    except Exception as e:
        logger.error(f"SAGA MIGRATION: Error creando tabla saga_logs: {e}")
        raise

if __name__ == "__main__":
    # Ejecutar migración
    logging.basicConfig(level=logging.INFO)
    crear_tabla_saga_logs()
