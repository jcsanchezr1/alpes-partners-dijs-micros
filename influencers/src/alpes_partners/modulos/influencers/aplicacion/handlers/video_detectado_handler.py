"""
Handler para procesar eventos de video detectado.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any

from ....dominio.eventos import VideoDetectado
from ....dominio.repositorios import RepositorioInfluencers
from ....infraestructura.repositorio_sqlalchemy import RepositorioInfluencersSQLAlchemy
from ....infraestructura.fabricas import FabricaInfluencers
from ....aplicacion.mapeadores import MapeadorInfluencer
from ....aplicacion.dto import RegistrarInfluencerDTO
from ....dominio.objetos_valor import Plataforma, DatosAudiencia
from ....dominio.excepciones import InfluencerNoEncontrado
from ....seedwork.infraestructura.uow import UnidadTrabajoPuerto

logger = logging.getLogger(__name__)


class VideoDetectadoHandler:
    """Handler para procesar eventos de video detectado."""
    
    def __init__(self):
        self.repositorio: RepositorioInfluencers = RepositorioInfluencersSQLAlchemy()
        self.fabrica_influencers = FabricaInfluencers()
    
    def procesar_video_detectado(self, evento: VideoDetectado) -> None:
        """
        Procesa un evento de video detectado.
        Si el influencer no existe, lo crea automáticamente.
        
        Args:
            evento: Evento de video detectado
        """
        logger.info(f"VIDEO HANDLER: Procesando video detectado - Video ID: {evento.video_id}, Influencer ID: {evento.influencer_id}")
        
        try:
            # Buscar el influencer
            influencer = self.repositorio.obtener_por_id(evento.influencer_id)
            
            if not influencer:
                # Crear influencer si no existe
                logger.info(f"VIDEO HANDLER: Influencer no encontrado, creando nuevo - ID: {evento.influencer_id}")
                influencer = self._crear_influencer_desde_evento(evento)
                logger.info(f"VIDEO HANDLER: Influencer creado exitosamente - ID: {influencer.id}")
            else:
                logger.info(f"VIDEO HANDLER: Influencer encontrado - ID: {influencer.id}")
            
            # Procesar el video detectado
            self._actualizar_metricas_influencer(influencer, evento)
            
            # Actualizar en el repositorio
            self.repositorio.actualizar(influencer)
            
            logger.info(f"VIDEO HANDLER: Video procesado exitosamente - Video ID: {evento.video_id}")
            
        except Exception as e:
            logger.error(f"VIDEO HANDLER: Error procesando video detectado: {e}")
            raise
    
    def _crear_influencer_desde_evento(self, evento: VideoDetectado):
        """
        Crea un nuevo influencer basado en los datos del evento de video detectado.
        
        Args:
            evento: Evento de video detectado con datos del influencer
            
        Returns:
            Influencer: Influencer creado
        """
        logger.info(f"VIDEO HANDLER: Creando influencer desde evento - Video ID: {evento.video_id}")
        
        try:
            # Validar que tenemos los datos mínimos necesarios
            if not evento.influencer_nombre:
                raise ValueError("Nombre del influencer es requerido para crear el influencer")
            
            if not evento.influencer_email:
                raise ValueError("Email del influencer es requerido para crear el influencer")
            
            # Crear DTO para el influencer
            influencer_dto = RegistrarInfluencerDTO(
                fecha_actualizacion=datetime.utcnow().isoformat(),
                fecha_creacion=datetime.utcnow().isoformat(),
                id=evento.influencer_id,  # Usar el ID del evento
                nombre=evento.influencer_nombre,
                email=evento.influencer_email,
                categorias=evento.influencer_categorias or [],
                descripcion=evento.influencer_descripcion or "",
                biografia=evento.influencer_biografia or "",
                sitio_web=evento.influencer_sitio_web or "",
                telefono=evento.influencer_telefono or ""
            )
            
            # Crear la entidad influencer
            influencer = self.fabrica_influencers.crear_objeto(influencer_dto, MapeadorInfluencer())
            influencer.crear_influencer(influencer)
            
            # Persistir el influencer usando UoW
            UnidadTrabajoPuerto.registrar_batch(self.repositorio.agregar, influencer)
            UnidadTrabajoPuerto.savepoint()
            UnidadTrabajoPuerto.commit()
            
            logger.info(f"VIDEO HANDLER: Influencer creado y persistido - ID: {influencer.id}, Nombre: {influencer.nombre}")
            
            return influencer
            
        except Exception as e:
            logger.error(f"VIDEO HANDLER: Error creando influencer desde evento: {e}")
            raise
    
    def _actualizar_metricas_influencer(self, influencer, evento: VideoDetectado) -> None:
        """
        Actualiza las métricas del influencer basado en el video detectado.
        
        Args:
            influencer: Entidad del influencer
            evento: Evento de video detectado
        """
        logger.info(f"VIDEO HANDLER: Actualizando métricas para influencer {influencer.id}")
        
        try:
            # Determinar la plataforma
            plataforma = Plataforma(evento.plataforma)
            
            # Crear o actualizar datos de audiencia para la plataforma
            if plataforma in influencer.audiencia_por_plataforma:
                # Actualizar datos existentes
                datos_audiencia = influencer.audiencia_por_plataforma[plataforma]
                # Aquí podrías actualizar métricas basadas en el video
                logger.info(f"VIDEO HANDLER: Actualizando audiencia existente para {plataforma.value}")
            else:
                # Crear nuevos datos de audiencia
                datos_audiencia = DatosAudiencia(
                    plataforma=plataforma,
                    seguidores=0,  # Se actualizará cuando se obtengan datos reales
                    engagement_rate=0.0,
                    alcance_promedio=0
                )
                influencer.audiencia_por_plataforma[plataforma] = datos_audiencia
                logger.info(f"VIDEO HANDLER: Creando nueva audiencia para {plataforma.value}")
            
            # Actualizar métricas generales
            influencer.metricas.campanas_completadas += 1
            
            # Aquí podrías agregar más lógica de negocio:
            # - Actualizar engagement basado en el video
            # - Calcular CPM basado en el video
            # - Actualizar ingresos generados
            # - Analizar el contenido del video para categorías
            
            logger.info(f"VIDEO HANDLER: Métricas actualizadas para influencer {influencer.id}")
            
        except Exception as e:
            logger.error(f"VIDEO HANDLER: Error actualizando métricas: {e}")
            raise


def procesar_evento_video_detectado(evento_data: Dict[str, Any]) -> None:
    """
    Función de conveniencia para procesar eventos de video detectado.
    
    Args:
        evento_data: Datos del evento en formato diccionario
    """
    try:
        # Extraer datos del influencer
        data = evento_data.get('data', {})
        influencer_categorias = []
        if data.get('influencer_categorias'):
            try:
                # Si es un string JSON, parsearlo
                if isinstance(data['influencer_categorias'], str):
                    influencer_categorias = json.loads(data['influencer_categorias'])
                else:
                    influencer_categorias = data['influencer_categorias']
            except (json.JSONDecodeError, TypeError):
                influencer_categorias = []
        
        # Crear evento de dominio desde los datos
        evento = VideoDetectado(
            video_id=data.get('video_id', ''),
            influencer_id=data.get('influencer_id', ''),
            plataforma=data.get('plataforma', ''),
            url_video=data.get('url_video', ''),
            titulo=data.get('titulo', ''),
            descripcion=data.get('descripcion'),
            duracion_segundos=data.get('duracion_segundos', 0),
            fecha_deteccion=datetime.fromisoformat(data.get('fecha_deteccion', datetime.utcnow().isoformat())),
            metadatos=data.get('metadatos', {}),
            # Datos del influencer
            influencer_nombre=data.get('influencer_nombre'),
            influencer_email=data.get('influencer_email'),
            influencer_categorias=influencer_categorias,
            influencer_descripcion=data.get('influencer_descripcion'),
            influencer_biografia=data.get('influencer_biografia'),
            influencer_sitio_web=data.get('influencer_sitio_web'),
            influencer_telefono=data.get('influencer_telefono')
        )
        
        # Procesar el evento
        handler = VideoDetectadoHandler()
        handler.procesar_video_detectado(evento)
        
    except Exception as e:
        logger.error(f"VIDEO HANDLER: Error procesando evento de video detectado: {e}")
        raise
