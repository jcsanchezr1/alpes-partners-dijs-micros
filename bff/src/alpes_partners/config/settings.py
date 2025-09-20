from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación BFF."""
    
    # Aplicación
    app_name: str = "BFF Microservice"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8004
    
    # Eventos
    eventos_topico_influencers: str = "eventos-crear-influencer"
    pulsar_address: str = "pulsar"  # Variable de entorno PULSAR_ADDRESS
    pulsar_broker: str = "pulsar:6650"  # Valor por defecto
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
