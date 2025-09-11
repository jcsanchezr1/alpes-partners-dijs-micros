# Importar comandos para registrarlos automáticamente
from .comandos.crear_contrato import CrearContrato

# Configurar handlers de integración
from pydispatch import dispatcher
from .handlers import HandlerContratoIntegracion
from ..dominio.eventos import ContratoCreado

dispatcher.connect(HandlerContratoIntegracion.handle_contrato_creado, signal=f'{ContratoCreado.__name__}Integracion')