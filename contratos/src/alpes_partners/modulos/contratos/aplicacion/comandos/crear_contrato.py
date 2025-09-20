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
from ...infraestructura.despachadores import DespachadorContratos
from ...infraestructura.schema.v1.eventos import EventoContratoCreado, ContratoCreadoPayload, EventoContratoError, ContratoErrorPayload
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime

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
        
        try:
            # Crear repositorio para validaciones de dominio
            repositorio = self.fabrica_repositorio.crear_objeto(RepositorioContratosSQLAlchemy)
            
            # Crear la entidad
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
            
            # VALIDACIÓN DE DOMINIO: Verificar que no exista un contrato activo DENTRO de la transacción
            logger.info(f"COMANDO HANDLER: Verificando contratos existentes dentro de la transacción")
            logger.info(f"COMANDO HANDLER: Buscando contrato con email: {comando.influencer_email}")
            
            existe_contrato = repositorio.existe_contrato_activo(comando.influencer_email)
            logger.info(f"COMANDO HANDLER: Resultado de validación: {existe_contrato}")
            
            if existe_contrato:
                logger.warning(f"COMANDO HANDLER: Ya existe un contrato activo para {comando.influencer_email}")
                raise ContratoYaExiste(f"Ya existe un contrato activo para este influencer")
            
            logger.info(f"COMANDO HANDLER: No hay conflictos de contratos")
            
            UnidadTrabajoPuerto.commit()
            
            logger.info(f"COMANDO HANDLER: Contrato creado exitosamente - ID: {comando.id}")
            
        except IntegrityError as e:
            logger.error(f"COMANDO HANDLER: Error de integridad en base de datos: {e}")
            # Publicar evento de error para el saga
            self._publicar_evento_error_contrato(comando, str(e))
            raise
            
        except Exception as e:
            logger.error(f"COMANDO HANDLER: Error inesperado: {e}")
            # Publicar evento de error para el saga
            self._publicar_evento_error_contrato(comando, str(e))
            raise
    
    def _publicar_evento_error_contrato(self, comando: CrearContrato, error: str):
        """Publica un evento de error cuando falla la creación del contrato."""
        try:
            logger.info(f"COMANDO HANDLER: Publicando evento de error de contrato")
            
            # Crear payload del evento de error
            payload = ContratoErrorPayload(
                id_contrato=comando.id,
                id_influencer=comando.influencer_id,
                id_campana=comando.campana_id,
                monto_total=comando.monto_base,
                moneda=comando.moneda,
                tipo_contrato=comando.tipo_contrato,
                fecha_creacion=comando.fecha_creacion,
                error=error,
                error_detalle=f"Error en creación de contrato: {error}"
            )
            
            # Crear evento de integración
            evento = EventoContratoError(
                id=str(uuid.uuid4()),
                time=datetime.utcnow(),
                ingestion=datetime.utcnow(),
                specversion="v1",
                type="ContratoError",
                datacontenttype="AVRO",
                service_name="contratos",
                data=payload
            )
            
            # Publicar evento
            despachador = DespachadorContratos()
            from pulsar.schema import AvroSchema
            despachador.publicar(evento, "eventos-contratos-error", AvroSchema(EventoContratoError))
            
            logger.info(f"COMANDO HANDLER: Evento de error publicado exitosamente")
            
        except Exception as e:
            logger.error(f"COMANDO HANDLER: Error publicando evento de error: {e}")


@comando.register(CrearContrato)
def ejecutar_comando_crear_contrato(comando: CrearContrato):
    handler = CrearContratoHandler()
    handler.handle(comando)
