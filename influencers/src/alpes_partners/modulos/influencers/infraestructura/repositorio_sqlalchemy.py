import logging
from typing import List, Optional
from sqlalchemy import and_, or_, func

from ..dominio.repositorios import RepositorioInfluencers
from ..dominio.entidades import Influencer
from ..dominio.objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma
from .modelos import InfluencerModelo
from .mappers import InfluencerMapper

# Importar db como en el tutorial
from ....seedwork.infraestructura.database import db

logger = logging.getLogger(__name__)


class RepositorioInfluencersSQLAlchemy(RepositorioInfluencers):
    """Implementación SQLAlchemy del repositorio de influencers."""
    
    def __init__(self):
        # Sin parámetros, usa db.session directamente como en el tutorial
        pass
    
    def obtener_por_id(self, id: str) -> Optional[Influencer]:
        """Obtiene un influencer por ID."""
        logger.info(f" REPOSITORIO: Buscando influencer por ID: {id}")
        
        modelo = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.id == id
        ).first()
        
        if modelo:
            logger.info(f" REPOSITORIO: Influencer encontrado: {modelo.nombre}")
            return InfluencerMapper.a_entidad(modelo)
        
        logger.info(f" REPOSITORIO: Influencer no encontrado: {id}")
        return None
    
    def obtener_por_email(self, email: str) -> Optional[Influencer]:
        """Obtiene un influencer por email."""
        logger.info(f" REPOSITORIO: Buscando influencer por email: {email}")
        
        modelo = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.email == email
        ).first()
        
        if modelo:
            logger.info(f" REPOSITORIO: Influencer encontrado: {modelo.nombre}")
            return InfluencerMapper.a_entidad(modelo)
        
        return None
    
    def agregar(self, entidad: Influencer) -> None:
        """Agrega un influencer."""
        logger.info(f" REPOSITORIO: Agregando influencer - ID: {entidad.id}, Email: {entidad.email.valor}")
        
        modelo = InfluencerMapper.a_modelo(entidad)
        logger.info(f" REPOSITORIO: Modelo SQLAlchemy creado - ID: {modelo.id}")
        
        db.session.add(modelo)
        logger.info(f" REPOSITORIO: Influencer agregado a la sesión - ID: {modelo.id}")
        
        if modelo in db.session.new:
            logger.info(f" REPOSITORIO: Confirmado - El modelo está en session.new")
        else:
            logger.warning(f" REPOSITORIO: PROBLEMA - El modelo NO está en session.new")
    
    def actualizar(self, entidad: Influencer) -> None:
        """Actualiza un influencer."""
        logger.info(f" REPOSITORIO: Actualizando influencer - ID: {entidad.id}")
        
        modelo = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.id == entidad.id
        ).first()
        
        if modelo:
            InfluencerMapper.actualizar_modelo(modelo, entidad)
            logger.info(f" REPOSITORIO: Influencer actualizado - ID: {entidad.id}")
        else:
            logger.warning(f" REPOSITORIO: Influencer no encontrado para actualizar: {entidad.id}")
            raise ValueError(f"Influencer con ID {entidad.id} no encontrado")
    
    def eliminar(self, id: str) -> None:
        """Elimina un influencer."""
        logger.info(f" REPOSITORIO: Eliminando influencer - ID: {id}")
        
        modelo = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.id == id
        ).first()
        
        if modelo:
            db.session.delete(modelo)
            logger.info(f" REPOSITORIO: Influencer eliminado - ID: {id}")
        else:
            logger.warning(f" REPOSITORIO: Influencer no encontrado para eliminar: {id}")
    
    def obtener_todos(self) -> List[Influencer]:
        """Obtiene todos los influencers."""
        logger.info(" REPOSITORIO: Obteniendo todos los influencers")
        
        modelos = db.session.query(InfluencerModelo).all()
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados")
        return influencers
    
    def obtener_por_estado(self, estado: EstadoInfluencer) -> List[Influencer]:
        """Obtiene influencers por estado."""
        logger.info(f" REPOSITORIO: Buscando influencers por estado: {estado.value}")
        
        modelos = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.estado == estado.value
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados con estado {estado.value}")
        return influencers
    
    def obtener_por_tipo(self, tipo: TipoInfluencer) -> List[Influencer]:
        """Obtiene influencers por tipo."""
        logger.info(f" REPOSITORIO: Buscando influencers por tipo: {tipo.value}")
        
        modelos = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.tipo_principal == tipo.value
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados con tipo {tipo.value}")
        return influencers
    
    def obtener_por_categoria(self, categoria: str) -> List[Influencer]:
        """Obtiene influencers que manejan una categoría específica."""
        logger.info(f" REPOSITORIO: Buscando influencers por categoría: {categoria}")
        
        # Buscar en el JSON de categorías
        modelos = db.session.query(InfluencerModelo).filter(
            func.json_array_length(InfluencerModelo.categorias) > 0
        ).all()
        
        # Filtrar en Python para búsqueda más precisa
        influencers_filtrados = []
        for modelo in modelos:
            if categoria.lower() in [cat.lower() for cat in modelo.categorias]:
                influencers_filtrados.append(InfluencerMapper.a_entidad(modelo))
        
        logger.info(f" REPOSITORIO: {len(influencers_filtrados)} influencers encontrados con categoría {categoria}")
        return influencers_filtrados
    
    def obtener_por_plataforma(self, plataforma: Plataforma) -> List[Influencer]:
        """Obtiene influencers que están en una plataforma específica."""
        logger.info(f" REPOSITORIO: Buscando influencers por plataforma: {plataforma.value}")
        
        # Buscar en el JSON de plataformas activas
        modelos = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.plataformas_activas.contains([plataforma.value])
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados en {plataforma.value}")
        return influencers
    
    def buscar_por_nombre(self, nombre: str) -> List[Influencer]:
        """Busca influencers por nombre (búsqueda parcial)."""
        logger.info(f" REPOSITORIO: Buscando influencers por nombre: {nombre}")
        
        modelos = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.nombre.ilike(f"%{nombre}%")
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados con nombre similar a '{nombre}'")
        return influencers
    
    def obtener_por_rango_seguidores(self, min_seguidores: int, max_seguidores: int) -> List[Influencer]:
        """Obtiene influencers dentro de un rango de seguidores."""
        logger.info(f" REPOSITORIO: Buscando influencers con {min_seguidores}-{max_seguidores} seguidores")
        
        modelos = db.session.query(InfluencerModelo).filter(
            and_(
                InfluencerModelo.total_seguidores >= min_seguidores,
                InfluencerModelo.total_seguidores <= max_seguidores
            )
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados en rango de seguidores")
        return influencers
    
    def obtener_por_engagement_minimo(self, engagement_minimo: float) -> List[Influencer]:
        """Obtiene influencers con engagement mínimo."""
        logger.info(f" REPOSITORIO: Buscando influencers con engagement >= {engagement_minimo}%")
        
        modelos = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.engagement_promedio >= engagement_minimo
        ).all()
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados con engagement >= {engagement_minimo}%")
        return influencers
    
    def existe_email(self, email: str) -> bool:
        """Verifica si existe un influencer con el email dado."""
        logger.info(f" REPOSITORIO: Verificando existencia de email: {email}")
        
        existe = db.session.query(InfluencerModelo).filter(
            InfluencerModelo.email == email
        ).first() is not None
        
        logger.info(f" REPOSITORIO: Email {'existe' if existe else 'no existe'}: {email}")
        return existe
    
    def obtener_con_filtros(self, 
                           estado: Optional[EstadoInfluencer] = None,
                           tipo: Optional[TipoInfluencer] = None,
                           categoria: Optional[str] = None,
                           plataforma: Optional[Plataforma] = None,
                           min_seguidores: Optional[int] = None,
                           max_seguidores: Optional[int] = None,
                           engagement_minimo: Optional[float] = None,
                           limite: int = 100,
                           offset: int = 0) -> List[Influencer]:
        """Obtiene influencers con múltiples filtros."""
        logger.info(" REPOSITORIO: Aplicando filtros múltiples")
        
        query = db.session.query(InfluencerModelo)
        
        # Aplicar filtros
        if estado:
            query = query.filter(InfluencerModelo.estado == estado.value)
        
        if tipo:
            query = query.filter(InfluencerModelo.tipo_principal == tipo.value)
        
        if min_seguidores is not None:
            query = query.filter(InfluencerModelo.total_seguidores >= min_seguidores)
        
        if max_seguidores is not None:
            query = query.filter(InfluencerModelo.total_seguidores <= max_seguidores)
        
        if engagement_minimo is not None:
            query = query.filter(InfluencerModelo.engagement_promedio >= engagement_minimo)
        
        if plataforma:
            query = query.filter(InfluencerModelo.plataformas_activas.contains([plataforma.value]))
        
        # Aplicar paginación
        query = query.offset(offset).limit(limite)
        
        modelos = query.all()
        
        # Filtrar por categoría en Python (más preciso)
        if categoria:
            modelos_filtrados = []
            for modelo in modelos:
                if categoria.lower() in [cat.lower() for cat in modelo.categorias]:
                    modelos_filtrados.append(modelo)
            modelos = modelos_filtrados
        
        influencers = [InfluencerMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f" REPOSITORIO: {len(influencers)} influencers encontrados con filtros aplicados")
        return influencers
