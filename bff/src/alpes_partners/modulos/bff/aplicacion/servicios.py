"""
Servicios de aplicación para el BFF.
"""

import logging
from typing import List
from ..infraestructura.pulsar_service import PulsarService
from alpes_partners.config.settings import settings

logger = logging.getLogger(__name__)


class BFFService:
    """Servicio principal del BFF."""
    
    def __init__(self):
        # Usar la variable de entorno PULSAR_ADDRESS si está disponible
        pulsar_host = settings.pulsar_address
        pulsar_broker = f"{pulsar_host}:6650"
        logger.info(f"Configurando Pulsar con broker: {pulsar_broker}")
        self.pulsar_service = PulsarService(pulsar_broker)
    
    def crear_influencer(
        self, 
        id_influencer: str, 
        nombre: str, 
        email: str, 
        categorias: List[str],
        plataformas: List[str] = None,
        descripcion: str = "",
        biografia: str = "",
        sitio_web: str = "",
        telefono: str = ""
    ) -> dict:
        """
        Crea un influencer enviando un evento al topic de influencers.
        
        Args:
            id_influencer: ID único del influencer
            nombre: Nombre del influencer
            email: Email del influencer
            categorias: Lista de categorías del influencer
            plataformas: Lista de plataformas del influencer (opcional)
            descripcion: Descripción del influencer (opcional)
            biografia: Biografía del influencer (opcional)
            sitio_web: Sitio web del influencer (opcional)
            telefono: Teléfono del influencer (opcional)
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            logger.info(f"Creando influencer: {id_influencer}")
            
            # Enviar evento a Pulsar
            self.pulsar_service.enviar_evento_crear_influencer(
                id_influencer=id_influencer,
                nombre=nombre,
                email=email,
                categorias=categorias,
                descripcion=descripcion,
                biografia=biografia,
                sitio_web=sitio_web,
                telefono=telefono
            )
            
            return {
                "success": True,
                "message": "Influencer procesado"
            }
            
        except Exception as e:
            logger.error(f"Error creando influencer: {e}")
            return {
                "success": False,
                "message": f"Error creando influencer: {str(e)}"
            }
    
    def cerrar_conexiones(self):
        """Cierra todas las conexiones."""
        self.pulsar_service.cerrar()
