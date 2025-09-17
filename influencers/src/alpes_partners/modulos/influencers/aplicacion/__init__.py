# Importar comandos para registrarlos automáticamente
from .comandos import registrar_influencer

# Configurar handlers de integración
from pydispatch import dispatcher
from .handlers import HandlerInfluencerIntegracion
from ..dominio.eventos import InfluencerRegistrado

dispatcher.connect(HandlerInfluencerIntegracion.handle_influencer_registrado, signal=f'{InfluencerRegistrado.__name__}Integracion')

# Importar saga solo cuando se necesite (lazy loading)
# La saga se registrará cuando se importe explícitamente
try:
    from ...sagas.aplicacion.coordinadores import saga_reservas
    print("SAGA: Handlers de saga registrados exitosamente")
except ImportError as e:
    print(f"SAGA: Saga no disponible (dependencias faltantes): {e}")
except Exception as e:
    print(f"SAGA: Error cargando saga: {e}")