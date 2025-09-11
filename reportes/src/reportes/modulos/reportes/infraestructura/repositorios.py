"""
Implementación de repositorios para reportes usando SQLAlchemy.
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

from reportes.modulos.reportes.dominio.repositorios import RepositorioReportes
from reportes.modulos.reportes.dominio.entidades import Reporte
from reportes.modulos.reportes.dominio.objetos_valor import (
    TipoReporte, EstadoReporte, MetadatosReporte, ConfiguracionReporte
)
from .schema.reportes import Reportes as ReporteSchema, EstadoReporteEnum, TipoReporteEnum

# Importar db como en el tutorial
from reportes.seedwork.infraestructura.database import db


class RepositorioReportesSQLAlchemy(RepositorioReportes):
    """Implementación del repositorio de reportes usando SQLAlchemy."""
    
    def __init__(self):
        # Sin parámetros, usa db.session directamente como en el tutorial
        pass
    
    async def obtener_por_id(self, id: str) -> Optional[Reporte]:
        """Obtiene un reporte por su ID."""
        schema = db.session.query(ReporteSchema).filter(ReporteSchema.id == id).first()
        if schema:
            return self._schema_a_entidad(schema)
        return None
    
    def obtener_por_id(self, reporte_id: str) -> Optional[Reporte]:
        """Obtiene un reporte por su ID (versión síncrona)."""
        schema = db.session.query(ReporteSchema).filter(ReporteSchema.id == reporte_id).first()
        if schema:
            return self._schema_a_entidad(schema)
        return None
    
    async def obtener_por_estado(self, estado: EstadoReporte) -> List[Reporte]:
        """Obtiene reportes por estado."""
        estado_enum = EstadoReporteEnum(estado.value)
        schemas = db.session.query(ReporteSchema).filter(
            ReporteSchema.estado == estado_enum
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    async def obtener_por_tipo(self, tipo: TipoReporte) -> List[Reporte]:
        """Obtiene reportes por tipo."""
        tipo_enum = TipoReporteEnum(tipo.value)
        schemas = db.session.query(ReporteSchema).filter(
            ReporteSchema.tipo_reporte == tipo_enum
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    async def obtener_por_origen_evento(self, origen_evento: str) -> List[Reporte]:
        """Obtiene reportes por origen del evento."""
        schemas = db.session.query(ReporteSchema).filter(
            ReporteSchema.origen_evento == origen_evento
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    async def buscar_por_nombre(self, nombre: str) -> List[Reporte]:
        """Busca reportes por nombre (búsqueda parcial)."""
        schemas = db.session.query(ReporteSchema).filter(
            ReporteSchema.nombre.ilike(f'%{nombre}%')
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    async def obtener_todos(self) -> List[Reporte]:
        """Obtiene todos los reportes."""
        schemas = db.session.query(ReporteSchema).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    async def agregar(self, entidad: Reporte) -> None:
        """Agrega un nuevo reporte."""
        logger.info(f"REPORTES: Agregando reporte '{entidad.nombre}' al repositorio")
        schema = self._entidad_a_schema(entidad)
        db.session.add(schema)
        db.session.flush()  # Para obtener el ID generado
        logger.info(f"REPORTES: Reporte '{entidad.nombre}' agregado a la sesión con ID: {schema.id}")
    
    def agregar(self, reporte: Reporte) -> None:
        """Agrega un nuevo reporte (versión síncrona)."""
        logger.info(f"REPORTES: Agregando reporte '{reporte.nombre}' al repositorio")
        schema = self._entidad_a_schema(reporte)
        db.session.add(schema)
        db.session.flush()  # Para obtener el ID generado
        logger.info(f"REPORTES: Reporte '{reporte.nombre}' agregado a la sesión con ID: {schema.id}")
    
    async def actualizar(self, entidad: Reporte) -> None:
        """Actualiza un reporte existente."""
        schema = db.session.query(ReporteSchema).filter(ReporteSchema.id == entidad.id).first()
        if schema:
            self._actualizar_schema_desde_entidad(schema, entidad)
            db.session.flush()
    
    def actualizar(self, reporte: Reporte) -> None:
        """Actualiza un reporte existente (versión síncrona)."""
        schema = db.session.query(ReporteSchema).filter(ReporteSchema.id == reporte.id).first()
        if schema:
            self._actualizar_schema_desde_entidad(schema, reporte)
            db.session.flush()
    
    async def eliminar(self, entidad: Reporte) -> None:
        """Elimina un reporte."""
        schema = db.session.query(ReporteSchema).filter(ReporteSchema.id == entidad.id).first()
        if schema:
            db.session.delete(schema)
            db.session.flush()
    
    def existe_con_nombre(self, nombre: str, excluir_id: Optional[str] = None) -> bool:
        """Verifica si existe un reporte con el nombre dado."""
        query = db.session.query(ReporteSchema).filter(ReporteSchema.nombre == nombre)
        if excluir_id:
            query = query.filter(ReporteSchema.id != excluir_id)
        return query.first() is not None
    
    def _schema_a_entidad(self, schema: ReporteSchema) -> Reporte:
        """Convierte un schema de base de datos a entidad de dominio."""
        
        # Crear objetos valor
        tipo_reporte = TipoReporte(schema.tipo_reporte.value)
        estado = EstadoReporte(schema.estado.value)
        
        # Metadatos
        metadatos_data = schema.metadatos or {}
        metadatos = MetadatosReporte(
            origen_evento=schema.origen_evento,
            version_esquema=metadatos_data.get('version_esquema', '1.0'),
            datos_adicionales=metadatos_data.get('datos_adicionales', {})
        )
        
        # Configuración
        config_data = schema.configuracion or {}
        configuracion = ConfiguracionReporte(
            incluir_metricas=config_data.get('incluir_metricas', True),
            formato_salida=config_data.get('formato_salida', 'json'),
            notificar_completado=config_data.get('notificar_completado', False)
        )
        
        # Crear la entidad
        reporte = Reporte(
            nombre=schema.nombre,
            descripcion=schema.descripcion,
            tipo_reporte=tipo_reporte,
            datos_origen=schema.datos_origen,
            metadatos=metadatos,
            configuracion=configuracion,
            id=str(schema.id)
        )
        
        # Establecer estado y fechas
        reporte.estado = estado
        reporte.fecha_creacion = schema.fecha_creacion
        reporte.fecha_actualizacion = schema.fecha_actualizacion
        
        # Establecer versión
        reporte.version = schema.version
        
        return reporte
    
    def _entidad_a_schema(self, reporte: Reporte) -> ReporteSchema:
        """Convierte una entidad de dominio a schema de base de datos."""
        
        # Preparar datos JSON
        metadatos_data = {
            'version_esquema': reporte.metadatos.version_esquema,
            'datos_adicionales': reporte.metadatos.datos_adicionales
        }
        
        configuracion_data = {
            'incluir_metricas': reporte.configuracion.incluir_metricas,
            'formato_salida': reporte.configuracion.formato_salida,
            'notificar_completado': reporte.configuracion.notificar_completado
        }
        
        return ReporteSchema(
            id=reporte.id,
            nombre=reporte.nombre,
            descripcion=reporte.descripcion,
            tipo_reporte=TipoReporteEnum(reporte.tipo_reporte.value),
            estado=EstadoReporteEnum(reporte.estado.value),
            datos_origen=reporte.datos_origen,
            origen_evento=reporte.metadatos.origen_evento,
            metadatos=metadatos_data,
            configuracion=configuracion_data,
            fecha_creacion=reporte.fecha_creacion,
            fecha_actualizacion=reporte.fecha_actualizacion,
            version=reporte.version
        )
    
    def _actualizar_schema_desde_entidad(self, schema: ReporteSchema, reporte: Reporte) -> None:
        """Actualiza un schema existente con datos de la entidad."""
        
        # Actualizar campos básicos
        schema.nombre = reporte.nombre
        schema.descripcion = reporte.descripcion
        schema.tipo_reporte = TipoReporteEnum(reporte.tipo_reporte.value)
        schema.estado = EstadoReporteEnum(reporte.estado.value)
        schema.datos_origen = reporte.datos_origen
        schema.origen_evento = reporte.metadatos.origen_evento
        
        # Actualizar datos JSON
        schema.metadatos = {
            'version_esquema': reporte.metadatos.version_esquema,
            'datos_adicionales': reporte.metadatos.datos_adicionales
        }
        
        schema.configuracion = {
            'incluir_metricas': reporte.configuracion.incluir_metricas,
            'formato_salida': reporte.configuracion.formato_salida,
            'notificar_completado': reporte.configuracion.notificar_completado
        }
        
        # Actualizar fechas
        schema.fecha_actualizacion = reporte.fecha_actualizacion
        schema.version = reporte.version
