"""
Implementación de repositorios para campanas usando SQLAlchemy.
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

from alpes_partners.modulos.campanas.dominio.repositorios import RepositorioCampanas
from alpes_partners.modulos.campanas.dominio.entidades import Campana
from alpes_partners.modulos.campanas.dominio.objetos_valor import (
    TipoComision, EstadoCampana, TerminosComision, PeriodoCampana,
    MaterialPromocional, CriteriosAfiliado, MetricasCampana
)
from alpes_partners.seedwork.dominio.objetos_valor import Dinero
from .schema.campanas import Campanas as CampanaSchema, EstadoCampanaEnum, TipoComisionEnum

# Importar db como en el tutorial
from alpes_partners.seedwork.infraestructura.database import db


class RepositorioCampanasSQLAlchemy(RepositorioCampanas):
    """Implementación del repositorio de campanas usando SQLAlchemy."""
    
    def __init__(self):
        # Sin parámetros, usa db.session directamente como en el tutorial
        pass
    
    def obtener_por_id(self, campana_id: str) -> Optional[Campana]:
        """Obtiene una campana por su ID."""
        schema = db.session.query(CampanaSchema).filter(CampanaSchema.id == campana_id).first()
        if schema:
            return self._schema_a_entidad(schema)
        return None
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Campana]:
        """Obtiene una campana por su nombre."""
        schema = db.session.query(CampanaSchema).filter(CampanaSchema.nombre == nombre).first()
        if schema:
            return self._schema_a_entidad(schema)
        return None
    
    def obtener_activas(self) -> List[Campana]:
        """Obtiene todas las campanas activas."""
        schemas = db.session.query(CampanaSchema).filter(
            CampanaSchema.estado == EstadoCampanaEnum.ACTIVA
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    def obtener_por_categoria(self, categoria: str) -> List[Campana]:
        """Obtiene campanas que incluyan una categoría específica."""
        # Buscar en el JSON de criterios_afiliado
        schemas = db.session.query(CampanaSchema).filter(
            CampanaSchema.criterios_afiliado.op('->>')('categorias_requeridas').like(f'%{categoria}%')
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    def obtener_por_influencer_origen(self, influencer_id: str) -> List[Campana]:
        """Obtiene campanas creadas para un influencer específico."""
        schemas = db.session.query(CampanaSchema).filter(
            CampanaSchema.influencer_origen_id == influencer_id
        ).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    def obtener_todas(self, limite: int = 100, offset: int = 0) -> List[Campana]:
        """Obtiene todas las campanas con paginación."""
        schemas = db.session.query(CampanaSchema).offset(offset).limit(limite).all()
        return [self._schema_a_entidad(schema) for schema in schemas]
    
    def agregar(self, campana: Campana) -> None:
        """Agrega una nueva campana."""
        logger.info(f"CAMPANAS: Agregando campana '{campana.nombre}' al repositorio")
        schema = self._entidad_a_schema(campana)
        db.session.add(schema)
        db.session.flush()  # Para obtener el ID generado
        logger.info(f"CAMPANAS: Campana '{campana.nombre}' agregada a la sesión con ID: {schema.id}")
    
    def actualizar(self, campana: Campana) -> None:
        """Actualiza una campana existente."""
        schema = db.session.query(CampanaSchema).filter(CampanaSchema.id == campana.id).first()
        if schema:
            self._actualizar_schema_desde_entidad(schema, campana)
            db.session.flush()
    
    def eliminar(self, campana_id: str) -> None:
        """Elimina una campana."""
        schema = db.session.query(CampanaSchema).filter(CampanaSchema.id == campana_id).first()
        if schema:
            db.session.delete(schema)
            db.session.flush()
    
    def existe_con_nombre(self, nombre: str, excluir_id: Optional[str] = None) -> bool:
        """Verifica si existe una campana con el nombre dado."""
        query = db.session.query(CampanaSchema).filter(CampanaSchema.nombre == nombre)
        if excluir_id:
            query = query.filter(CampanaSchema.id != excluir_id)
        return query.first() is not None
    
    def _schema_a_entidad(self, schema: CampanaSchema) -> Campana:
        """Convierte un schema de base de datos a entidad de dominio."""
        
        # Crear objetos valor
        tipo_comision = TipoComision(schema.tipo_comision.value)
        dinero_comision = Dinero(schema.valor_comision, schema.moneda)
        terminos_comision = TerminosComision(
            tipo_comision, 
            dinero_comision, 
            schema.descripcion_comision or ""
        )
        
        periodo = PeriodoCampana(schema.fecha_inicio, schema.fecha_fin)
        
        # Material promocional
        material_data = schema.material_promocional or {}
        material = MaterialPromocional(
            titulo=material_data.get('titulo', ''),
            descripcion=material_data.get('descripcion', ''),
            enlaces=material_data.get('enlaces', []),
            imagenes=material_data.get('imagenes', []),
            banners=material_data.get('banners', [])
        )
        
        # Criterios de afiliado
        criterios_data = schema.criterios_afiliado or {}
        criterios = CriteriosAfiliado(
            tipos_permitidos=criterios_data.get('tipos_permitidos', []),
            categorias_requeridas=criterios_data.get('categorias_requeridas', []),
            paises_permitidos=criterios_data.get('paises_permitidos', []),
            metricas_minimas=criterios_data.get('metricas_minimas', {})
        )
        
        # Crear la entidad
        campana = Campana(
            nombre=schema.nombre,
            descripcion=schema.descripcion,
            terminos_comision=terminos_comision,
            periodo=periodo,
            material_promocional=material,
            criterios_afiliado=criterios,
            id=str(schema.id)
        )
        
        # Establecer estado y fechas
        campana.estado = EstadoCampana(schema.estado.value)
        campana.fecha_activacion = schema.fecha_activacion
        campana.fecha_pausa = schema.fecha_pausa
        
        # Métricas
        metricas_data = schema.metricas or {}
        campana.metricas = MetricasCampana(
            afiliados_asignados=metricas_data.get('afiliados_asignados', 0),
            clics_totales=metricas_data.get('clics_totales', 0),
            conversiones_totales=metricas_data.get('conversiones_totales', 0),
            inversion_total=metricas_data.get('inversion_total', 0.0),
            ingresos_generados=metricas_data.get('ingresos_generados', 0.0)
        )
        
        # Afiliados asignados
        campana.afiliados_asignados = set(schema.afiliados_asignados or [])
        
        # Establecer versión
        campana.version = schema.version
        
        return campana
    
    def _entidad_a_schema(self, campana: Campana) -> CampanaSchema:
        """Convierte una entidad de dominio a schema de base de datos."""
        
        # Preparar datos JSON
        material_data = {
            'titulo': campana.material_promocional.titulo,
            'descripcion': campana.material_promocional.descripcion,
            'enlaces': campana.material_promocional.enlaces,
            'imagenes': campana.material_promocional.imagenes,
            'banners': campana.material_promocional.banners
        }
        
        criterios_data = {
            'tipos_permitidos': campana.criterios_afiliado.tipos_permitidos,
            'categorias_requeridas': campana.criterios_afiliado.categorias_requeridas,
            'paises_permitidos': campana.criterios_afiliado.paises_permitidos,
            'metricas_minimas': campana.criterios_afiliado.metricas_minimas
        }
        
        metricas_data = {
            'afiliados_asignados': campana.metricas.afiliados_asignados,
            'clics_totales': campana.metricas.clics_totales,
            'conversiones_totales': campana.metricas.conversiones_totales,
            'inversion_total': campana.metricas.inversion_total,
            'ingresos_generados': campana.metricas.ingresos_generados
        }
        
        return CampanaSchema(
            id=campana.id,
            nombre=campana.nombre,
            descripcion=campana.descripcion,
            tipo_comision=TipoComisionEnum(campana.terminos_comision.tipo.value),
            valor_comision=campana.terminos_comision.valor.cantidad,
            moneda=campana.terminos_comision.valor.moneda,
            descripcion_comision=campana.terminos_comision.descripcion,
            fecha_inicio=campana.periodo.fecha_inicio,
            fecha_fin=campana.periodo.fecha_fin,
            estado=EstadoCampanaEnum(campana.estado.value),
            fecha_activacion=campana.fecha_activacion,
            fecha_pausa=campana.fecha_pausa,
            material_promocional=material_data,
            criterios_afiliado=criterios_data,
            metricas=metricas_data,
            afiliados_asignados=list(campana.afiliados_asignados),
            version=campana.version
        )
    
    def _actualizar_schema_desde_entidad(self, schema: CampanaSchema, campana: Campana) -> None:
        """Actualiza un schema existente con datos de la entidad."""
        
        # Actualizar campos básicos
        schema.nombre = campana.nombre
        schema.descripcion = campana.descripcion
        schema.tipo_comision = TipoComisionEnum(campana.terminos_comision.tipo.value)
        schema.valor_comision = campana.terminos_comision.valor.cantidad
        schema.moneda = campana.terminos_comision.valor.moneda
        schema.descripcion_comision = campana.terminos_comision.descripcion
        schema.fecha_inicio = campana.periodo.fecha_inicio
        schema.fecha_fin = campana.periodo.fecha_fin
        schema.estado = EstadoCampanaEnum(campana.estado.value)
        schema.fecha_activacion = campana.fecha_activacion
        schema.fecha_pausa = campana.fecha_pausa
        
        # Actualizar datos JSON
        schema.material_promocional = {
            'titulo': campana.material_promocional.titulo,
            'descripcion': campana.material_promocional.descripcion,
            'enlaces': campana.material_promocional.enlaces,
            'imagenes': campana.material_promocional.imagenes,
            'banners': campana.material_promocional.banners
        }
        
        schema.criterios_afiliado = {
            'tipos_permitidos': campana.criterios_afiliado.tipos_permitidos,
            'categorias_requeridas': campana.criterios_afiliado.categorias_requeridas,
            'paises_permitidos': campana.criterios_afiliado.paises_permitidos,
            'metricas_minimas': campana.criterios_afiliado.metricas_minimas
        }
        
        schema.metricas = {
            'afiliados_asignados': campana.metricas.afiliados_asignados,
            'clics_totales': campana.metricas.clics_totales,
            'conversiones_totales': campana.metricas.conversiones_totales,
            'inversion_total': campana.metricas.inversion_total,
            'ingresos_generados': campana.metricas.ingresos_generados
        }
        
        schema.afiliados_asignados = list(campana.afiliados_asignados)
        schema.version = campana.version
