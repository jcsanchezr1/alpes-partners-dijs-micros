import logging
from typing import List, Optional

from ....seedwork.aplicacion.handlers import ManejadorComando
from ....seedwork.infraestructura.uow import UnidadTrabajo
from ..dominio.repositorios import RepositorioContratos
from ..dominio.entidades import Contrato
from ..dominio.excepciones import ContratoYaExiste
from ..dominio.eventos import ContratoCreado
from ..infraestructura.despachadores import DespachadorContratos

from .comandos.crear_contrato import CrearContrato

logger = logging.getLogger(__name__)


class HandlerContratoIntegracion:
    """Handler para eventos de integración de contratos."""
    
    @staticmethod
    def handle_contrato_creado(evento):
        """Handler para evento ContratoCreado de integración."""
        try:
            despachador = DespachadorContratos()
            despachador.publicar_evento_contrato_creado(evento, 'eventos-contratos')
            logger.info(f"EVENTO: ContratoCreado publicado exitosamente - ID: {getattr(evento, 'contrato_id', 'N/A')}")
        except Exception as e:
            logger.error(f"ERROR: No se pudo publicar evento ContratoCreado: {e}")