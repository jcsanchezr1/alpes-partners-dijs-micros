import logging
from typing import List, Optional

from ....seedwork.aplicacion.handlers import ManejadorComando
from ....seedwork.infraestructura.uow import UnidadTrabajo
from ..dominio.repositorios import RepositorioInfluencers
from ..dominio.entidades import Influencer
from ..dominio.excepciones import EmailYaRegistrado
from ..dominio.eventos import InfluencerRegistrado
from ..infraestructura.despachadores import DespachadorInfluencers

from .comandos.registrar_influencer import RegistrarInfluencer

logger = logging.getLogger(__name__)


class HandlerInfluencerIntegracion:
    """Handler para eventos de integración de influencers."""
    
    @staticmethod
    def handle_influencer_registrado(evento):
        """Handler para evento InfluencerRegistrado de integración."""
        despachador = DespachadorInfluencers()
        despachador.publicar_evento_influencer_registrado(evento, 'eventos-influencers')


logger.info("HANDLERS: Handlers de aplicación de influencers cargados")