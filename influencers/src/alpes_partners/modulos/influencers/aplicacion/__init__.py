# Importar comandos para registrarlos automáticamente
from .comandos import registrar_influencer

# Configurar handlers de integración
from pydispatch import dispatcher
from .handlers import HandlerInfluencerIntegracion
from ..dominio.eventos import InfluencerRegistrado

dispatcher.connect(HandlerInfluencerIntegracion.handle_influencer_registrado, signal=f'{InfluencerRegistrado.__name__}Integracion')