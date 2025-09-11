from typing import Optional, Dict, Any
from dataclasses import dataclass
from reportes.seedwork.aplicacion.comandos import Comando
from ..dto import CrearReporteDTO
from .base import RegistrarReporteBaseHandler
from reportes.seedwork.aplicacion.comandos import ejecutar_commando as comando

from ...dominio.entidades import Reporte
from reportes.seedwork.infraestructura.uow import UnidadTrabajoPuerto
from ..mapeadores import MapeadorReporte
from ...infraestructura.repositorios import RepositorioReportesSQLAlchemy
from ...dominio.excepciones import ExcepcionReporteYaExiste

import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistrarReporte(Comando):
    """Comando para registrar un nuevo reporte."""
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo_reporte: str
    datos_origen: Dict[str, Any]
    origen_evento: str
    estado: str = "activo"  # Campo para manejo de compensación
    version_esquema: str = "1.0"
    datos_adicionales: Optional[Dict[str, Any]] = None
    incluir_metricas: bool = True
    formato_salida: str = "json"
    notificar_completado: bool = False
    campana_origen_id: Optional[str] = None
    contrato_origen_id: Optional[str] = None


class RegistrarReporteHandler(RegistrarReporteBaseHandler):
    
    def handle(self, comando: RegistrarReporte):
        logger.info(f"COMANDO HANDLER: Iniciando creación de reporte - Nombre: {comando.nombre}")
        
        # Crear repositorio para validaciones de dominio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReportesSQLAlchemy.__class__)
        
        # VALIDACIÓN DE DOMINIO: Verificar unicidad del nombre ANTES de crear la entidad
        logger.info(f"COMANDO HANDLER: Verificando unicidad del nombre: {comando.nombre}")
        if repositorio.existe_con_nombre(comando.nombre):
            logger.warning(f"COMANDO HANDLER: Nombre ya registrado: {comando.nombre}")
            raise ExcepcionReporteYaExiste(f"Ya existe un reporte con el nombre {comando.nombre}")
        
        logger.info(f"COMANDO HANDLER: Nombre disponible: {comando.nombre}")
        
        # Crear la entidad solo después de validar las reglas de dominio
        reporte_dto = CrearReporteDTO(
            fecha_actualizacion=comando.fecha_actualizacion,
            fecha_creacion=comando.fecha_creacion,
            id=comando.id,
            nombre=comando.nombre,
            descripcion=comando.descripcion,
            tipo_reporte=comando.tipo_reporte,
            datos_origen=comando.datos_origen,
            origen_evento=comando.origen_evento,
            estado=comando.estado,  # Campo para compensación
            version_esquema=comando.version_esquema,
            datos_adicionales=comando.datos_adicionales,
            incluir_metricas=comando.incluir_metricas,
            formato_salida=comando.formato_salida,
            notificar_completado=comando.notificar_completado
        )

        reporte: Reporte = self.fabrica_reportes.crear_objeto(reporte_dto, MapeadorReporte())

        # Usar el sistema de UoW con batches y eventos (como en el tutorial)
        UnidadTrabajoPuerto.registrar_batch(repositorio.agregar, reporte)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        
        logger.info(f"COMANDO HANDLER: Reporte creado exitosamente - ID: {comando.id}")


@comando.register(RegistrarReporte)
def ejecutar_comando_registrar_reporte(comando: RegistrarReporte):
    handler = RegistrarReporteHandler()
    handler.handle(comando)
