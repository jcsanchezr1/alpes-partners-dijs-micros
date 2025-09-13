from .....seedwork.aplicacion.comandos import ComandoHandler
from ...infraestructura.fabricas import FabricaRepositorioCampanas
from ...dominio.fabricas import FabricaCampanas

class RegistrarCampanaBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorioCampanas = FabricaRepositorioCampanas()
        self._fabrica_campanas: FabricaCampanas = FabricaCampanas()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_campanas(self):
        return self._fabrica_campanas
