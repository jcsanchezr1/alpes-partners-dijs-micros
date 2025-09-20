from dataclasses import dataclass
from typing import Optional
from .....seedwork.aplicacion.comandos import Comando
from ..dto import EliminarCampanaDTO
from .base import EliminarCampanaBaseHandler
from .....seedwork.aplicacion.comandos import ejecutar_commando as comando

from ...dominio.entidades import Campana
from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ...infraestructura.repositorios import RepositorioCampanasSQLAlchemy
from ...dominio.excepciones import CampanaNoExisteExcepcion

import logging

logger = logging.getLogger(__name__)


@dataclass
class EliminarCampana(Comando):
    """Comando para eliminar una campaña."""
    campana_id: str
    influencer_id: Optional[str] = None  # Opcional para compensación
    razon: str = "Compensación por falla en saga"


class EliminarCampanaHandler(EliminarCampanaBaseHandler):
    
    def handle(self, comando: EliminarCampana):
        logger.info(f"COMANDO HANDLER: Eliminando campaña - ID: {comando.campana_id}")
        logger.info(f"COMANDO HANDLER: Razón: {comando.razon}")
        if comando.influencer_id:
            logger.info(f"COMANDO HANDLER: Influencer ID: {comando.influencer_id}")
        else:
            logger.info(f"COMANDO HANDLER: Sin influencer ID (compensación)")
        
        try:
            # Crear DTO
            dto = EliminarCampanaDTO(
                campana_id=comando.campana_id,
                influencer_id=comando.influencer_id,
                razon=comando.razon
            )
            
            # Ejecutar lógica de negocio
            self._eliminar_campana(dto)
            
            # Publicar evento de eliminación
            self._publicar_evento_eliminacion(comando)
            
            logger.info(f"COMANDO HANDLER: Campaña eliminada exitosamente - ID: {comando.campana_id}")
            
        except Exception as e:
            logger.error(f"COMANDO HANDLER: Error eliminando campaña: {e}")
            raise


@comando.register(EliminarCampana)
def ejecutar_comando_eliminar_campana(comando: EliminarCampana):
    """Ejecutar comando de eliminar campaña."""
    handler = EliminarCampanaHandler()
    return handler.handle(comando)
