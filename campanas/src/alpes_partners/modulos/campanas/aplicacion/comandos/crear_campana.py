from typing import Optional, List
from dataclasses import dataclass, field
from .....seedwork.aplicacion.comandos import Comando
from ..dto import RegistrarCampanaDTO
from .base import RegistrarCampanaBaseHandler
from .....seedwork.aplicacion.comandos import ejecutar_commando as comando

from ...dominio.entidades import Campana
from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ..mapeadores import MapeadorCampana
from ...infraestructura.repositorios import RepositorioCampanasSQLAlchemy
from ...dominio.excepciones import CampanaYaExisteExcepcion

import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistrarCampana(Comando):
    """Comando para registrar una nueva campana."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo_comision: str
    valor_comision: float
    moneda: str
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    titulo_material: str = ""
    descripcion_material: str = ""
    categorias_objetivo: List[str] = None
    tipos_afiliado_permitidos: List[str] = None
    paises_permitidos: List[str] = None
    enlaces_material: List[str] = None
    imagenes_material: List[str] = None
    banners_material: List[str] = None
    metricas_minimas: dict = None
    auto_activar: bool = False
    influencer_origen_id: Optional[str] = None
    categoria_origen: Optional[str] = None
    # Datos del influencer para eventos
    influencer_origen_nombre: Optional[str] = None
    influencer_origen_email: Optional[str] = None


class RegistrarCampanaHandler(RegistrarCampanaBaseHandler):
    
    def handle(self, comando: RegistrarCampana):
        logger.info(f"COMANDO HANDLER: Iniciando registro de campana - Nombre: {comando.nombre}")
        
        # Crear repositorio para validaciones de dominio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioCampanasSQLAlchemy)
        
        # VALIDACIÓN DE DOMINIO: Verificar unicidad del nombre ANTES de crear la entidad
        logger.info(f"COMANDO HANDLER: Verificando unicidad del nombre: {comando.nombre}")
        if repositorio.existe_con_nombre(comando.nombre):
            logger.warning(f"COMANDO HANDLER: Nombre ya registrado: {comando.nombre}")
            raise CampanaYaExisteExcepcion(f"Ya existe una campana con el nombre {comando.nombre}")
        
        logger.info(f"COMANDO HANDLER: Nombre disponible: {comando.nombre}")
        
        # DEBUG: Mostrar datos del influencer en el comando
        logger.info(f"COMANDO HANDLER: Datos del influencer en comando:")
        logger.info(f"  - influencer_origen_id: {comando.influencer_origen_id}")
        logger.info(f"  - influencer_origen_nombre: {comando.influencer_origen_nombre}")
        logger.info(f"  - influencer_origen_email: {comando.influencer_origen_email}")
        
        # Crear la entidad solo después de validar las reglas de dominio
        campana_dto = RegistrarCampanaDTO(
                fecha_actualizacion=comando.fecha_actualizacion
            ,   fecha_creacion=comando.fecha_creacion
            ,   id=comando.id
            ,   nombre=comando.nombre
            ,   descripcion=comando.descripcion
            ,   tipo_comision=comando.tipo_comision
            ,   valor_comision=comando.valor_comision
            ,   moneda=comando.moneda
            ,   fecha_inicio=comando.fecha_inicio
            ,   fecha_fin=comando.fecha_fin
            ,   titulo_material=comando.titulo_material
            ,   descripcion_material=comando.descripcion_material
            ,   categorias_objetivo=comando.categorias_objetivo
            ,   tipos_afiliado_permitidos=comando.tipos_afiliado_permitidos
            ,   paises_permitidos=comando.paises_permitidos
            ,   enlaces_material=comando.enlaces_material
            ,   imagenes_material=comando.imagenes_material
            ,   banners_material=comando.banners_material
            ,   metricas_minimas=comando.metricas_minimas
            ,   auto_activar=comando.auto_activar
            ,   influencer_origen_id=comando.influencer_origen_id
            ,   categoria_origen=comando.categoria_origen
            ,   influencer_origen_nombre=comando.influencer_origen_nombre
            ,   influencer_origen_email=comando.influencer_origen_email)

        campana: Campana = self.fabrica_campanas.crear_objeto(campana_dto, MapeadorCampana())

        logger.info(f"COMANDO HANDLER: Datos del influencer en la entidad creada:")
        logger.info(f"  - influencer_origen_id: {campana.influencer_origen_id}")
        logger.info(f"  - influencer_origen_nombre: {campana.influencer_origen_nombre}")
        logger.info(f"  - influencer_origen_email: {campana.influencer_origen_email}")

        campana.emitir_evento_creacion()

        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, campana)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        
        logger.info(f"COMANDO HANDLER: Campana registrada exitosamente - ID: {comando.id}")


@comando.register(RegistrarCampana)
def ejecutar_comando_registrar_campana(comando: RegistrarCampana):
    handler = RegistrarCampanaHandler()
    handler.handle(comando)