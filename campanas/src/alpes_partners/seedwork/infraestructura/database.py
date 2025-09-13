from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from ...config.settings import settings

# Para Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Instancia global de SQLAlchemy para Flask
db = SQLAlchemy()

logger = logging.getLogger(__name__)

# Motor de base de datos síncrono
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Para evitar problemas con conexiones en desarrollo
    echo=settings.debug,  # Log de queries SQL en modo debug
)

# Factory de sesiones síncronas
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_db_session() -> Generator[Session, None, None]:
    """Generador de sesiones de base de datos síncronas."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Inicializa la base de datos creando las tablas."""
    # Importar todos los modelos para que se registren en Base.metadata
    
    from ...modulos.campanas.infraestructura.schema.campanas import Campanas
    
    logger.info("Modelos registrados:")
    
    logger.info(f"   - Campanas: {len([t for t in Campanas.metadata.tables.keys() if 'campana' in t.lower()])} tablas")
    logger.info(f"   - Total tablas: {len(Campanas.metadata.tables)} tablas")
    
    # Solo recrear tablas si está explícitamente configurado
    if settings.recreate_db:
        logger.warning("RECREANDO BASE DE DATOS - Se perderán todos los datos")
        Campanas.metadata.drop_all(bind=engine)
        Campanas.metadata.create_all(bind=engine)
        logger.info("Base de datos recreada completamente")
    else:
        # Solo crear las tablas si no existen (preservar datos)
        Campanas.metadata.create_all(bind=engine)
        logger.info("Tablas de base de datos creadas/actualizadas (datos preservados)")


def init_db_flask_tables():
    """Inicializa las tablas usando Flask-SQLAlchemy."""
    # Importar todos los modelos
    from ...modulos.campanas.infraestructura.schema.campanas import Campanas
    
    # Crear todas las tablas definidas en los modelos
    Campanas.metadata.create_all(bind=engine)
    logger.info("Tablas Flask-SQLAlchemy creadas/actualizadas")


def init_db_flask(app):
    """Inicializa la base de datos para Flask."""
    db.init_app(app)
    logger.info("Base de datos Flask inicializada")


def close_db():
    """Cierra las conexiones de base de datos."""
    engine.dispose()
    logger.info("Conexiones de base de datos cerradas")
