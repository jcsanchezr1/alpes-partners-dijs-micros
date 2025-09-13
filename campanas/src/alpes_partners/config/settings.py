from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Base de datos
    database_url: str = "postgresql://postgres:postgres@localhost:5432/alpespartners_dijs"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Aplicación
    app_name: str = "Campanas Microservice"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    
    # Eventos
    eventos_topico_influencers: str = "eventos-influencers"
    eventos_topico_campanas: str = "eventos-campanas"
    
    # Logging
    log_level: str = "INFO"
    
    # Base de datos - Control de recreación
    recreate_db: bool = False  # Si es True, elimina y recrea las tablas
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
