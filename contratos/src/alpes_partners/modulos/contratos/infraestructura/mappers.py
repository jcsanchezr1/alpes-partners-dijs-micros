import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..dominio.entidades import Contrato
from ..dominio.objetos_valor import (
    TipoContrato, EstadoContrato, TerminosContrato, 
    MetricasContrato, CategoriaContrato, DatosAudiencia,
    Demografia, Plataforma, Genero, RangoEdad, PeriodoContrato,
    CompensacionContrato, InfluencerContrato, CampanaContrato
)
from ....seedwork.dominio.objetos_valor import Email, Telefono, Dinero
from .modelos import ContratoModelo

logger = logging.getLogger(__name__)


class ContratoMapper:
    """Mapper para convertir entre entidades de dominio y modelos SQLAlchemy."""
    
    @staticmethod
    def a_modelo(contrato: Contrato) -> ContratoModelo:
        """Convierte una entidad Contrato a modelo SQLAlchemy."""
        
        # Convertir estado a string
        estado_valor = contrato.estado.value if hasattr(contrato.estado, 'value') else str(contrato.estado)
        tipo_valor = contrato.tipo_contrato.value if hasattr(contrato.tipo_contrato, 'value') else str(contrato.tipo_contrato)
        
        logger.info(f"MAPPER: Convirtiendo entidad a modelo - ID: {contrato.id}, Estado: {estado_valor}")
        
        # Convertir audiencia por plataforma a JSON (del influencer)
        audiencia_json = {}
        total_seguidores = 0
        plataformas_principales = []
        
        for plataforma, datos in contrato.audiencia_por_plataforma.items():
            plataforma_key = plataforma.value if hasattr(plataforma, 'value') else str(plataforma)
            audiencia_json[plataforma_key] = {
                'seguidores': datos.seguidores,
                'engagement_rate': datos.engagement_rate,
                'alcance_promedio': datos.alcance_promedio
            }
            total_seguidores += datos.seguidores
            plataformas_principales.append(plataforma_key)
        
        # Convertir demografía a JSON
        demografia_json = None
        if contrato.demografia:
            demografia_json = {
                'distribucion_genero': {k.value: v for k, v in contrato.demografia.distribucion_genero.items()},
                'distribucion_edad': {k.value: v for k, v in contrato.demografia.distribucion_edad.items()},
                'paises_principales': contrato.demografia.paises_principales
            }
        
        return ContratoModelo(
            id=contrato.id,
            # Información del influencer
            influencer_id=contrato.influencer.influencer_id,
            influencer_nombre=contrato.influencer.nombre,
            influencer_email=contrato.influencer.email,
            # Información de la campaña
            campana_id=contrato.campana.campana_id,
            campana_nombre=contrato.campana.nombre,
            # Estado y tipo del contrato
            estado=estado_valor,
            tipo_contrato=tipo_valor,
            # Términos del contrato
            categorias=contrato.terminos.categorias.categorias,
            descripcion=contrato.terminos.descripcion,
            entregables=contrato.terminos.entregables,
            condiciones_especiales=contrato.terminos.condiciones_especiales,
            # Compensación económica
            monto_base=contrato.compensacion.monto_base.cantidad,
            moneda=contrato.compensacion.monto_base.moneda,
            tipo_compensacion=contrato.compensacion.tipo_compensacion,
            bonificaciones=contrato.compensacion.bonificaciones,
            # Métricas del contrato
            entregables_completados=contrato.metricas.entregables_completados,
            engagement_alcanzado=contrato.metricas.engagement_alcanzado,
            costo_total=contrato.metricas.costo_total,
            roi_obtenido=contrato.metricas.roi_obtenido,
            # Período del contrato
            fecha_inicio_contrato=contrato.periodo.fecha_inicio,
            fecha_fin_contrato=contrato.periodo.fecha_fin,
            duracion_dias=contrato.periodo.duracion_dias,
            # Campos calculados
            total_seguidores=total_seguidores,
            plataformas_principales=plataformas_principales,
            # Audiencia y demografía
            audiencia_por_plataforma=audiencia_json,
            demografia=demografia_json,
            # Fechas del contrato
            fecha_creacion=contrato.fecha_creacion,
            fecha_firma=contrato.fecha_firma,
            fecha_finalizacion=contrato.fecha_finalizacion,
            version=str(contrato.version)
        )
    
    @staticmethod
    def a_entidad(modelo: ContratoModelo) -> Contrato:
        """Convierte un modelo SQLAlchemy a entidad Contrato."""
        
        logger.info(f"MAPPER: Convirtiendo modelo a entidad - ID: {modelo.id}")
        
        # Crear objetos de valor
        influencer = InfluencerContrato(
            influencer_id=modelo.influencer_id,
            nombre=modelo.influencer_nombre,
            email=modelo.influencer_email,
            plataformas_principales=modelo.plataformas_principales or []
        )
        
        campana = CampanaContrato(
            campana_id=modelo.campana_id,
            nombre=modelo.campana_nombre
        )
        
        categorias = CategoriaContrato(modelo.categorias)
        terminos = TerminosContrato(
            categorias=categorias,
            descripcion=modelo.descripcion,
            entregables=modelo.entregables or "",
            condiciones_especiales=modelo.condiciones_especiales or ""
        )
        
        dinero = Dinero(modelo.monto_base, modelo.moneda)
        compensacion = CompensacionContrato(
            monto_base=dinero,
            tipo_compensacion=modelo.tipo_compensacion,
            bonificaciones=modelo.bonificaciones or {}
        )
        
        periodo = PeriodoContrato(
            fecha_inicio=modelo.fecha_inicio_contrato,
            fecha_fin=modelo.fecha_fin_contrato,
            duracion_dias=modelo.duracion_dias
        )
        
        # Determinar tipo de contrato
        try:
            tipo_contrato = TipoContrato(modelo.tipo_contrato)
        except ValueError:
            tipo_contrato = TipoContrato.PUNTUAL
        
        # Crear entidad
        contrato = Contrato(
            influencer=influencer,
            campana=campana,
            terminos=terminos,
            compensacion=compensacion,
            periodo=periodo,
            tipo_contrato=tipo_contrato,
            id=str(modelo.id)
        )
        
        # Establecer estado
        try:
            contrato.estado = EstadoContrato(modelo.estado)
        except ValueError:
            contrato.estado = EstadoContrato.BORRADOR
        
        # Establecer fechas
        contrato.fecha_creacion = modelo.fecha_creacion
        contrato.fecha_firma = modelo.fecha_firma
        contrato.fecha_finalizacion = modelo.fecha_finalizacion
        contrato.version = int(modelo.version) if modelo.version.isdigit() else 1
        
        # Reconstruir audiencia por plataforma
        if modelo.audiencia_por_plataforma:
            for plataforma_str, datos in modelo.audiencia_por_plataforma.items():
                try:
                    plataforma = Plataforma(plataforma_str)
                    datos_audiencia = DatosAudiencia(
                        plataforma=plataforma,
                        seguidores=datos.get('seguidores', 0),
                        engagement_rate=datos.get('engagement_rate', 0.0),
                        alcance_promedio=datos.get('alcance_promedio', 0)
                    )
                    contrato.audiencia_por_plataforma[plataforma] = datos_audiencia
                except ValueError:
                    logger.warning(f"MAPPER: Plataforma desconocida: {plataforma_str}")
        
        # Reconstruir demografía
        if modelo.demografia:
            try:
                distribucion_genero = {}
                for genero_str, porcentaje in modelo.demografia.get('distribucion_genero', {}).items():
                    try:
                        genero = Genero(genero_str)
                        distribucion_genero[genero] = porcentaje
                    except ValueError:
                        logger.warning(f"MAPPER: Género desconocido: {genero_str}")
                
                distribucion_edad = {}
                for edad_str, porcentaje in modelo.demografia.get('distribucion_edad', {}).items():
                    try:
                        edad = RangoEdad(edad_str)
                        distribucion_edad[edad] = porcentaje
                    except ValueError:
                        logger.warning(f"MAPPER: Rango de edad desconocido: {edad_str}")
                
                if distribucion_genero and distribucion_edad:
                    contrato.demografia = Demografia(
                        distribucion_genero=distribucion_genero,
                        distribucion_edad=distribucion_edad,
                        paises_principales=modelo.demografia.get('paises_principales', [])
                    )
            except Exception as e:
                logger.warning(f"MAPPER: Error al reconstruir demografía: {e}")
        
        # Establecer métricas
        contrato.metricas = MetricasContrato(
            entregables_completados=modelo.entregables_completados,
            engagement_alcanzado=modelo.engagement_alcanzado,
            costo_total=modelo.costo_total,
            roi_obtenido=modelo.roi_obtenido
        )
        
        # Limpiar eventos (no queremos re-emitir eventos al cargar desde BD)
        contrato.limpiar_eventos()
        
        return contrato
    
    @staticmethod
    def actualizar_modelo(modelo: ContratoModelo, contrato: Contrato) -> None:
        """Actualiza un modelo existente con datos de la entidad."""
        
        logger.info(f"MAPPER: Actualizando modelo existente - ID: {contrato.id}")
        
        # Actualizar información del influencer
        modelo.influencer_id = contrato.influencer.influencer_id
        modelo.influencer_nombre = contrato.influencer.nombre
        modelo.influencer_email = contrato.influencer.email
        
        # Actualizar información de la campaña
        modelo.campana_id = contrato.campana.campana_id
        modelo.campana_nombre = contrato.campana.nombre
        
        # Actualizar estado y tipo
        modelo.estado = contrato.estado.value if hasattr(contrato.estado, 'value') else str(contrato.estado)
        modelo.tipo_contrato = contrato.tipo_contrato.value if hasattr(contrato.tipo_contrato, 'value') else str(contrato.tipo_contrato)
        
        # Actualizar términos
        modelo.categorias = contrato.terminos.categorias.categorias
        modelo.descripcion = contrato.terminos.descripcion
        modelo.entregables = contrato.terminos.entregables
        modelo.condiciones_especiales = contrato.terminos.condiciones_especiales
        
        # Actualizar compensación
        modelo.monto_base = contrato.compensacion.monto_base.cantidad
        modelo.moneda = contrato.compensacion.monto_base.moneda
        modelo.tipo_compensacion = contrato.compensacion.tipo_compensacion
        modelo.bonificaciones = contrato.compensacion.bonificaciones
        
        # Actualizar métricas
        modelo.entregables_completados = contrato.metricas.entregables_completados
        modelo.engagement_alcanzado = contrato.metricas.engagement_alcanzado
        modelo.costo_total = contrato.metricas.costo_total
        modelo.roi_obtenido = contrato.metricas.roi_obtenido
        
        # Actualizar período
        modelo.fecha_inicio_contrato = contrato.periodo.fecha_inicio
        modelo.fecha_fin_contrato = contrato.periodo.fecha_fin
        modelo.duracion_dias = contrato.periodo.duracion_dias
        
        # Actualizar audiencia
        audiencia_json = {}
        total_seguidores = 0
        plataformas_principales = []
        
        for plataforma, datos in contrato.audiencia_por_plataforma.items():
            plataforma_key = plataforma.value if hasattr(plataforma, 'value') else str(plataforma)
            audiencia_json[plataforma_key] = {
                'seguidores': datos.seguidores,
                'engagement_rate': datos.engagement_rate,
                'alcance_promedio': datos.alcance_promedio
            }
            total_seguidores += datos.seguidores
            plataformas_principales.append(plataforma_key)
        
        modelo.audiencia_por_plataforma = audiencia_json
        modelo.total_seguidores = total_seguidores
        modelo.plataformas_principales = plataformas_principales
        
        # Actualizar demografía
        if contrato.demografia:
            modelo.demografia = {
                'distribucion_genero': {k.value: v for k, v in contrato.demografia.distribucion_genero.items()},
                'distribucion_edad': {k.value: v for k, v in contrato.demografia.distribucion_edad.items()},
                'paises_principales': contrato.demografia.paises_principales
            }
        
        # Actualizar fechas
        modelo.fecha_firma = contrato.fecha_firma
        modelo.fecha_finalizacion = contrato.fecha_finalizacion
        modelo.version = str(contrato.version)
        modelo.fecha_actualizacion = datetime.utcnow()