""" Mapeadores para la conversión de objetos en la capa de aplicación del dominio de influencers

En este archivo usted encontrará los diferentes mapeadores para convertir
objetos entre DTOs y entidades del dominio de influencers

"""

# Importaciones usando el path correcto para el contexto de ejecución
import sys
import os

# Agregar el directorio src al path si no está
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', '..', '..')
src_path = os.path.normpath(src_path)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from alpes_partners.seedwork.dominio.repositorios import Mapeador
from alpes_partners.modulos.influencers.dominio.entidades import Influencer
from alpes_partners.modulos.influencers.aplicacion.dto import RegistrarInfluencerDTO, InfluencerDTO

from datetime import datetime


class MapeadorInfluencer(Mapeador):
    """Mapeador para convertir entre DTOs e Influencers."""
    
    def obtener_tipo(self) -> type:
        return Influencer.__class__
    
    def entidad_a_dto(self, entidad: Influencer) -> InfluencerDTO:
        """Convierte una entidad Influencer a DTO."""
        
        # Obtener plataformas
        plataformas = [plat.value for plat in entidad.audiencia_por_plataforma.keys()]
        
        # Calcular tipo principal
        tipo_principal = None
        if entidad.obtener_tipo_principal():
            tipo_principal = entidad.obtener_tipo_principal().value
        
        # Convertir demografía si existe
        demografia_dto = None
        if entidad.demografia:
            from .dto import DemografiaDTO
            demografia_dto = DemografiaDTO(
                distribucion_genero=entidad.demografia.distribucion_genero,
                distribucion_edad=entidad.demografia.distribucion_edad,
                paises_principales=entidad.demografia.paises_principales
            )
        
        return InfluencerDTO(
            id=entidad.id,
            nombre=entidad.nombre,
            email=entidad.email.valor,
            estado=entidad.estado,
            categorias=entidad.perfil.categorias.categorias,
            descripcion=entidad.perfil.descripcion,
            biografia=entidad.perfil.biografia,
            sitio_web=entidad.perfil.sitio_web,
            telefono=entidad.telefono.numero if entidad.telefono else None,
            fecha_creacion=entidad.fecha_creacion.isoformat(),
            fecha_activacion=entidad.fecha_activacion.isoformat() if entidad.fecha_activacion else None,
            plataformas=plataformas,
            total_seguidores=entidad.obtener_total_seguidores(),
            engagement_promedio=entidad.obtener_engagement_promedio(),
            tipo_principal=tipo_principal,
            campanas_completadas=entidad.metricas.campanas_completadas,
            cpm_promedio=entidad.metricas.cpm_promedio,
            ingresos_generados=entidad.metricas.ingresos_generados,
            demografia=demografia_dto
        )
    
    def dto_a_entidad(self, dto: RegistrarInfluencerDTO) -> Influencer:
        """Convierte un DTO a entidad Influencer."""
        
        # Crear influencer usando el método de fábrica de la entidad
        influencer = Influencer.crear(
            nombre=dto.nombre,
            email=dto.email,
            categorias=dto.categorias,
            descripcion=dto.descripcion,
            biografia=dto.biografia,
            sitio_web=dto.sitio_web,
            telefono=dto.telefono
        )
        
        # Establecer el ID si viene en el DTO (para comandos)
        if hasattr(dto, 'id') and dto.id:
            influencer._id = dto.id
        
        return influencer
