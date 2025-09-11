from .....seedwork.aplicacion.comandos import ComandoHandler
from ...infraestructura.fabricas import FabricaRepositorioContratos
from ...dominio.fabricas import FabricaContratos

class CrearContratoBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorioContratos = FabricaRepositorioContratos()
        self._fabrica_contratos: FabricaContratos = FabricaContratos()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_contratos(self):
        return self._fabrica_contratos
