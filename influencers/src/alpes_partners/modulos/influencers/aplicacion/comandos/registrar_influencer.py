from typing import Optional, List
from dataclasses import dataclass, field
from .....seedwork.aplicacion.comandos import Comando
from ..dto import RegistrarInfluencerDTO
from .base import RegistrarInfluencerBaseHandler
from .....seedwork.aplicacion.comandos import ejecutar_commando as comando

from ...dominio.entidades import Influencer
from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ..mapeadores import MapeadorInfluencer
from ...infraestructura.repositorio_sqlalchemy import RepositorioInfluencersSQLAlchemy

import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistrarInfluencer(Comando):
    """Comando para registrar un nuevo influencer."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    email: str
    categorias: List[str]
    descripcion: Optional[str] = None
    biografia: Optional[str] = None
    sitio_web: Optional[str] = None
    telefono: Optional[str] = None


class RegistrarInfluencerHandler(RegistrarInfluencerBaseHandler):
    
    def handle(self, comando: RegistrarInfluencer):
        logger.info(f"COMANDO HANDLER: Iniciando registro de influencer - Email: {comando.email}")
        
        # Crear repositorio para validaciones de dominio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioInfluencersSQLAlchemy)

        logger.info(f"COMANDO HANDLER: Email disponible: {comando.email}")
        
        # Crear la entidad solo después de validar las reglas de dominio
        influencer_dto = RegistrarInfluencerDTO(
                fecha_actualizacion=comando.fecha_actualizacion
            ,   fecha_creacion=comando.fecha_creacion
            ,   id=comando.id
            ,   nombre=comando.nombre
            ,   email=comando.email
            ,   categorias=comando.categorias
            ,   descripcion=comando.descripcion
            ,   biografia=comando.biografia
            ,   sitio_web=comando.sitio_web
            ,   telefono=comando.telefono)

        influencer: Influencer = self.fabrica_influencers.crear_objeto(influencer_dto, MapeadorInfluencer())
        influencer.crear_influencer(influencer)

        # Usar el sistema de UoW con batches y eventos (como en el tutorial)
        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, influencer)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        
        logger.info(f"COMANDO HANDLER: Influencer registrado exitosamente - ID: {comando.id}")


@comando.register(RegistrarInfluencer)
def ejecutar_comando_registrar_influencer(comando: RegistrarInfluencer):
    handler = RegistrarInfluencerHandler()
    handler.handle(comando)