from .....seedwork.aplicacion.comandos import ComandoHandler
from ...infraestructura.fabricas import FabricaRepositorioInfluencers
from ...dominio.fabricas import FabricaInfluencers

class RegistrarInfluencerBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorioInfluencers = FabricaRepositorioInfluencers()
        self._fabrica_influencers: FabricaInfluencers = FabricaInfluencers()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_influencers(self):
        return self._fabrica_influencers
