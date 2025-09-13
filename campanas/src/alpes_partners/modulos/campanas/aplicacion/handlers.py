import logging

from ..dominio.eventos import CampanaCreada
from ..infraestructura.despachadores import DespachadorCampanas

logger = logging.getLogger(__name__)


class HandlerCampanaIntegracion:
    """Handler para eventos de integración de campanas."""
    
    @staticmethod
    def handle_campana_creada(evento):
        """Handler para evento CampanaCreada de integración."""
        try:
            despachador = DespachadorCampanas()
            despachador.publicar_evento_campana_creada(evento, 'eventos-campanas')
            logger.info(f"EVENTO: CampanaCreada publicado exitosamente - ID: {getattr(evento, 'campana_id', 'N/A')}")
        except Exception as e:
            logger.error(f"ERROR: No se pudo publicar evento CampanaCreada: {e}")


logger.info("HANDLERS: Handlers de aplicación de campanas cargados")
