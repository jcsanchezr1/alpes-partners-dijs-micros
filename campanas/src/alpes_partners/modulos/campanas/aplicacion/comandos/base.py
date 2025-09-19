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


class EliminarCampanaBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorioCampanas = FabricaRepositorioCampanas()

    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    def _eliminar_campana(self, dto):
        """Elimina una campaña del repositorio."""
        from ...dominio.excepciones import CampanaNoExisteExcepcion
        from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto
        from ...infraestructura.repositorios import RepositorioCampanasSQLAlchemy
        
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioCampanasSQLAlchemy)
        
        # Verificar que la campaña existe
        campana = repositorio.obtener_por_id(dto.campana_id)
        if not campana:
            raise CampanaNoExisteExcepcion(f"Campaña con ID {dto.campana_id} no existe")
        
        # Eliminar la campaña
        repositorio.eliminar(dto.campana_id)
        
        # Confirmar cambios
        uow = UnidadTrabajoPuerto()
        uow.commit()
    
    def _publicar_evento_eliminacion(self, comando):
        """Publica evento de eliminación de campaña."""
        from ...infraestructura.despachadores import DespachadorCampanas
        
        despachador = DespachadorCampanas()
        despachador.publicar_evento_campana_eliminada(
            campana_id=comando.campana_id,
            influencer_id=comando.influencer_id,
            razon=comando.razon
        )
