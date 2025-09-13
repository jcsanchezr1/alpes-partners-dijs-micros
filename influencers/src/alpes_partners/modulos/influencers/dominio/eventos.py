from datetime import datetime
from typing import List, Dict, Any, Optional
from ....seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma


class InfluencerRegistrado(EventoIntegracion):
    """Evento emitido cuando se registra un nuevo influencer."""
    
    def __init__(self, 
                 influencer_id: str,
                 nombre: str,
                 email: str,
                 categorias: List[str],
                 plataformas: List[str],
                 fecha_registro: datetime):
        super().__init__()
        self.influencer_id = influencer_id
        self.nombre = nombre
        self.email = email
        self.categorias = categorias
        self.plataformas = plataformas
        self.fecha_registro = fecha_registro


class VideoDetectado(EventoIntegracion):
    """Evento emitido cuando se detecta un video de un influencer."""
    
    def __init__(self, 
                 video_id: str,
                 influencer_id: str,
                 plataforma: str,
                 url_video: str,
                 titulo: str,
                 descripcion: Optional[str],
                 duracion_segundos: int,
                 fecha_deteccion: datetime,
                 metadatos: Dict[str, Any],
                 # Datos del influencer para creación automática
                 influencer_nombre: Optional[str] = None,
                 influencer_email: Optional[str] = None,
                 influencer_categorias: Optional[List[str]] = None,
                 influencer_descripcion: Optional[str] = None,
                 influencer_biografia: Optional[str] = None,
                 influencer_sitio_web: Optional[str] = None,
                 influencer_telefono: Optional[str] = None):
        super().__init__()
        self.video_id = video_id
        self.influencer_id = influencer_id
        self.plataforma = plataforma
        self.url_video = url_video
        self.titulo = titulo
        self.descripcion = descripcion
        self.duracion_segundos = duracion_segundos
        self.fecha_deteccion = fecha_deteccion
        self.metadatos = metadatos
        # Datos del influencer
        self.influencer_nombre = influencer_nombre
        self.influencer_email = influencer_email
        self.influencer_categorias = influencer_categorias or []
        self.influencer_descripcion = influencer_descripcion
        self.influencer_biografia = influencer_biografia
        self.influencer_sitio_web = influencer_sitio_web
        self.influencer_telefono = influencer_telefono