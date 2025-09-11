from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from .....seedwork.aplicacion.comandos import Comando
from ..dto import CrearContratoDTO
from .base import CrearContratoBaseHandler
from .....seedwork.aplicacion.comandos import ejecutar_commando as comando

from ...dominio.entidades import Contrato
from ...dominio.objetos_valor import TipoContrato
from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ..mapeadores import MapeadorContrato
from ...infraestructura.repositorio_sqlalchemy import RepositorioContratosSQLAlchemy
from ...dominio.excepciones import ContratoYaExiste

import logging

logger = logging.getLogger(__name__)


@dataclass
class CrearContrato(Comando):
    """Comando para crear un nuevo contrato."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    influencer_id: str
    influencer_nombre: str
    influencer_email: str
    campana_id: str
    campana_nombre: str
    categorias: List[str]
    descripcion: str
    monto_base: float
    moneda: str = "USD"
    fecha_inicio: str = None
    fecha_fin: Optional[str] = None
    entregables: Optional[str] = None
    tipo_contrato: str = "puntual"


class CrearContratoHandler(CrearContratoBaseHandler):
    
    def handle(self, comando: CrearContrato):
        logger.info(f"COMANDO HANDLER: Iniciando creación de contrato")
        logger.info(f"COMANDO HANDLER: Contrato: {comando.influencer_nombre}, Campaña: {comando.campana_nombre}")
        
        # Crear repositorio para validaciones de dominio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioContratosSQLAlchemy.__class__)
        
        # VALIDACIÓN DE DOMINIO: Verificar que no exista un contrato activo
        logger.info(f"COMANDO HANDLER: Verificando contratos existentes")
        if repositorio.existe_contrato_activo(comando.influencer_id, comando.campana_id):
            logger.warning(f"COMANDO HANDLER: Ya existe un contrato activo entre {comando.influencer_id} y {comando.campana_id}")
            raise ContratoYaExiste(f"Ya existe un contrato activo entre el influencer y la campaña")
        
        logger.info(f"COMANDO HANDLER: No hay conflictos de contratos")
        
        # Crear la entidad solo después de validar las reglas de dominio
        contrato_dto = CrearContratoDTO(
            fecha_actualizacion=comando.fecha_actualizacion,
            fecha_creacion=comando.fecha_creacion,
            id=comando.id,
            influencer_id=comando.influencer_id,
            influencer_nombre=comando.influencer_nombre,
            influencer_email=comando.influencer_email,
            campana_id=comando.campana_id,
            campana_nombre=comando.campana_nombre,
            categorias=comando.categorias,
            descripcion=comando.descripcion,
            monto_base=comando.monto_base,
            moneda=comando.moneda,
            fecha_inicio=comando.fecha_inicio,
            fecha_fin=comando.fecha_fin,
            entregables=comando.entregables,
            tipo_contrato=comando.tipo_contrato
        )

        contrato: Contrato = self.fabrica_contratos.crear_objeto(contrato_dto, MapeadorContrato())
        contrato.crear_contrato(contrato)

        # Usar el sistema de UoW con batches y eventos (como en el tutorial)
        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, contrato)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        
        logger.info(f"COMANDO HANDLER: Contrato creado exitosamente - ID: {comando.id}")


@comando.register(CrearContrato)
def ejecutar_comando_crear_contrato(comando: CrearContrato):
    handler = CrearContratoHandler()
    handler.handle(comando)
