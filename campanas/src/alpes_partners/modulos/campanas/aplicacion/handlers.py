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
            logger.info(f"EVENTO HANDLER: Procesando CampanaCreada - ID: {getattr(evento, 'campana_id', 'N/A')}")
            logger.info(f"EVENTO HANDLER: Datos del evento: {getattr(evento, '_datos_evento', lambda: {})()}")
            
            despachador = DespachadorCampanas()
            despachador.publicar_evento_campana_creada(evento, 'eventos-campanas')
            logger.info(f"EVENTO: CampanaCreada publicado exitosamente - ID: {getattr(evento, 'campana_id', 'N/A')}")
        except Exception as e:
            logger.error(f"ERROR: No se pudo publicar evento CampanaCreada: {e}")
            import traceback
            logger.error(f"ERROR: Traceback: {traceback.format_exc()}")


logger.info("HANDLERS: Handlers de aplicación de campanas cargados")
