# Importar comandos para registrarlos automáticamente
from .comandos.crear_campana import RegistrarCampana

# Configurar handlers de integración
from pydispatch import dispatcher
from .handlers import HandlerCampanaIntegracion
from ..dominio.eventos import CampanaCreada

dispatcher.connect(HandlerCampanaIntegracion.handle_campana_creada, signal=f'{CampanaCreada.__name__}Integracion')