from reportes.seedwork.aplicacion.comandos import ComandoHandler
from ...infraestructura.fabricas import FabricaRepositorioReportes
from ...dominio.fabricas import FabricaReportes


class RegistrarReporteBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorioReportes = FabricaRepositorioReportes()
        self._fabrica_reportes: FabricaReportes = FabricaReportes()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_reportes(self):
        return self._fabrica_reportes
