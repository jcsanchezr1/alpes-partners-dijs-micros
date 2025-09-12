from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Base de datos - Misma BD que contratos
    database_url: str = "postgresql://postgres:postgres@localhost:5432/alpespartners_dijs"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Aplicación
    app_name: str = "Reportes Microservice"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # Eventos
    eventos_topico_reportes: str = "eventos-reportes"
    eventos_topico_contratos: str = "eventos-contratos"  # Tópico principal del que consume
    
    # Logging
    log_level: str = "INFO"
    
    # Base de datos - Control de recreación
    recreate_db: bool = False  # Si es True, elimina y recrea las tablas
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
