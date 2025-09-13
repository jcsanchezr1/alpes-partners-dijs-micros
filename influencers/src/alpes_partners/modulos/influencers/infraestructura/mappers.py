import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..dominio.entidades import Influencer
from ..dominio.objetos_valor import (
    TipoInfluencer, EstadoInfluencer, PerfilInfluencer, 
    MetricasInfluencer, CategoriaInfluencer, DatosAudiencia,
    Demografia, Plataforma, Genero, RangoEdad
)
from ....seedwork.dominio.objetos_valor import Email, Telefono
from .modelos import InfluencerModelo

logger = logging.getLogger(__name__)


class InfluencerMapper:
    """Mapper para convertir entre entidades de dominio y modelos SQLAlchemy."""
    
    @staticmethod
    def a_modelo(influencer: Influencer) -> InfluencerModelo:
        """Convierte una entidad Influencer a modelo SQLAlchemy."""
        
        # Convertir estado a string
        estado_valor = influencer.estado.value if hasattr(influencer.estado, 'value') else str(influencer.estado)
        
        logger.info(f"MAPPER: Convirtiendo entidad a modelo - ID: {influencer.id}, Estado: {estado_valor}")
        
        # Convertir audiencia por plataforma a JSON
        audiencia_json = {}
        total_seguidores = 0
        plataformas_activas = []
        tipo_principal = None
        engagement_total = 0.0
        
        for plataforma, datos in influencer.audiencia_por_plataforma.items():
            plataforma_key = plataforma.value if hasattr(plataforma, 'value') else str(plataforma)
            audiencia_json[plataforma_key] = {
                'seguidores': datos.seguidores,
                'engagement_rate': datos.engagement_rate,
                'alcance_promedio': datos.alcance_promedio
            }
            total_seguidores += datos.seguidores
            plataformas_activas.append(plataforma_key)
            engagement_total += datos.engagement_rate
        
        # Calcular tipo principal basado en el total de seguidores
        if total_seguidores > 0:
            if total_seguidores < 10000:
                tipo_principal = TipoInfluencer.NANO.value
            elif total_seguidores < 100000:
                tipo_principal = TipoInfluencer.MICRO.value
            elif total_seguidores < 1000000:
                tipo_principal = TipoInfluencer.MACRO.value
            elif total_seguidores < 10000000:
                tipo_principal = TipoInfluencer.MEGA.value
            else:
                tipo_principal = TipoInfluencer.CELEBRITY.value
        
        # Calcular engagement promedio
        engagement_promedio_calculado = (engagement_total / len(influencer.audiencia_por_plataforma)) if influencer.audiencia_por_plataforma else 0.0
        
        # Convertir demografía a JSON
        demografia_json = None
        if influencer.demografia:
            demografia_json = {
                'distribucion_genero': {k.value: v for k, v in influencer.demografia.distribucion_genero.items()},
                'distribucion_edad': {k.value: v for k, v in influencer.demografia.distribucion_edad.items()},
                'paises_principales': influencer.demografia.paises_principales
            }
        
        return InfluencerModelo(
            id=influencer.id,
            nombre=influencer.nombre,
            email=influencer.email.valor,
            telefono=influencer.telefono.numero if influencer.telefono else None,
            estado=estado_valor,
            categorias=influencer.perfil.categorias.categorias,
            descripcion=influencer.perfil.descripcion,
            biografia=influencer.perfil.biografia,
            sitio_web=influencer.perfil.sitio_web,
            audiencia_por_plataforma=audiencia_json,
            demografia=demografia_json,
            campanas_completadas=influencer.metricas.campanas_completadas,
            engagement_promedio=engagement_promedio_calculado,
            cpm_promedio=influencer.metricas.cpm_promedio,
            ingresos_generados=influencer.metricas.ingresos_generados,
            total_seguidores=total_seguidores,
            tipo_principal=tipo_principal,
            plataformas_activas=plataformas_activas,
            fecha_creacion=influencer.fecha_creacion,
            fecha_activacion=influencer.fecha_activacion,
            fecha_desactivacion=influencer.fecha_desactivacion,
            version=str(influencer.version)
        )
    
    @staticmethod
    def a_entidad(modelo: InfluencerModelo) -> Influencer:
        """Convierte un modelo SQLAlchemy a entidad Influencer."""
        
        logger.info(f"MAPPER: Convirtiendo modelo a entidad - ID: {modelo.id}")
        
        # Crear objetos de valor básicos
        email = Email(modelo.email)
        telefono = Telefono(modelo.telefono) if modelo.telefono else None
        categorias = CategoriaInfluencer(modelo.categorias)
        
        # Crear perfil
        perfil = PerfilInfluencer(
            categorias=categorias,
            descripcion=modelo.descripcion,
            biografia=modelo.biografia or "",
            sitio_web=modelo.sitio_web or ""
        )
        
        # Crear entidad
        influencer = Influencer(
            nombre=modelo.nombre,
            email=email,
            perfil=perfil,
            telefono=telefono,
            id=str(modelo.id)
        )
        
        # Establecer estado
        try:
            influencer.estado = EstadoInfluencer(modelo.estado)
        except ValueError:
            influencer.estado = EstadoInfluencer.PENDIENTE
        
        # Establecer fechas
        influencer.fecha_creacion = modelo.fecha_creacion
        influencer.fecha_activacion = modelo.fecha_activacion
        influencer.fecha_desactivacion = modelo.fecha_desactivacion
        influencer.version = int(modelo.version) if modelo.version.isdigit() else 1
        
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
                    influencer.audiencia_por_plataforma[plataforma] = datos_audiencia
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
                    influencer.demografia = Demografia(
                        distribucion_genero=distribucion_genero,
                        distribucion_edad=distribucion_edad,
                        paises_principales=modelo.demografia.get('paises_principales', [])
                    )
            except Exception as e:
                logger.warning(f"MAPPER: Error al reconstruir demografía: {e}")
        
        # Establecer métricas
        influencer.metricas = MetricasInfluencer(
            campanas_completadas=modelo.campanas_completadas,
            engagement_promedio=modelo.engagement_promedio,
            cpm_promedio=modelo.cpm_promedio,
            ingresos_generados=modelo.ingresos_generados
        )
        
        # Limpiar eventos (no queremos re-emitir eventos al cargar desde BD)
        influencer.limpiar_eventos()
        
        return influencer
    
    @staticmethod
    def actualizar_modelo(modelo: InfluencerModelo, influencer: Influencer) -> None:
        """Actualiza un modelo existente con datos de la entidad."""
        
        logger.info(f"MAPPER: Actualizando modelo existente - ID: {influencer.id}")
        
        # Actualizar campos básicos
        modelo.nombre = influencer.nombre
        modelo.email = influencer.email.valor
        modelo.telefono = influencer.telefono.numero if influencer.telefono else None
        modelo.estado = influencer.estado.value if hasattr(influencer.estado, 'value') else str(influencer.estado)
        
        # Actualizar perfil
        modelo.categorias = influencer.perfil.categorias.categorias
        modelo.descripcion = influencer.perfil.descripcion
        modelo.biografia = influencer.perfil.biografia
        modelo.sitio_web = influencer.perfil.sitio_web
        
        # Actualizar audiencia
        audiencia_json = {}
        total_seguidores = 0
        plataformas_activas = []
        engagement_total = 0.0
        
        for plataforma, datos in influencer.audiencia_por_plataforma.items():
            plataforma_key = plataforma.value if hasattr(plataforma, 'value') else str(plataforma)
            audiencia_json[plataforma_key] = {
                'seguidores': datos.seguidores,
                'engagement_rate': datos.engagement_rate,
                'alcance_promedio': datos.alcance_promedio
            }
            total_seguidores += datos.seguidores
            plataformas_activas.append(plataforma_key)
            engagement_total += datos.engagement_rate
        
        modelo.audiencia_por_plataforma = audiencia_json
        modelo.total_seguidores = total_seguidores
        modelo.plataformas_activas = plataformas_activas
        
        # Calcular tipo principal
        if total_seguidores > 0:
            if total_seguidores < 10000:
                modelo.tipo_principal = TipoInfluencer.NANO.value
            elif total_seguidores < 100000:
                modelo.tipo_principal = TipoInfluencer.MICRO.value
            elif total_seguidores < 1000000:
                modelo.tipo_principal = TipoInfluencer.MACRO.value
            elif total_seguidores < 10000000:
                modelo.tipo_principal = TipoInfluencer.MEGA.value
            else:
                modelo.tipo_principal = TipoInfluencer.CELEBRITY.value
        
        # Actualizar métricas
        modelo.campanas_completadas = influencer.metricas.campanas_completadas
        modelo.engagement_promedio = (engagement_total / len(influencer.audiencia_por_plataforma)) if influencer.audiencia_por_plataforma else 0.0
        modelo.cpm_promedio = influencer.metricas.cpm_promedio
        modelo.ingresos_generados = influencer.metricas.ingresos_generados
        
        # Actualizar demografía
        if influencer.demografia:
            modelo.demografia = {
                'distribucion_genero': {k.value: v for k, v in influencer.demografia.distribucion_genero.items()},
                'distribucion_edad': {k.value: v for k, v in influencer.demografia.distribucion_edad.items()},
                'paises_principales': influencer.demografia.paises_principales
            }
        
        # Actualizar fechas
        modelo.fecha_activacion = influencer.fecha_activacion
        modelo.fecha_desactivacion = influencer.fecha_desactivacion
        modelo.version = str(influencer.version)
        modelo.fecha_actualizacion = datetime.utcnow()
