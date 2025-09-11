import logging
from typing import List, Optional
from sqlalchemy import and_, or_, func
from datetime import datetime

from ..dominio.repositorios import RepositorioContratos
from ..dominio.entidades import Contrato
from ..dominio.objetos_valor import TipoContrato, EstadoContrato, Plataforma
from .modelos import ContratoModelo
from .mappers import ContratoMapper

# Importar db como en el tutorial
from ....seedwork.infraestructura.database import db

logger = logging.getLogger(__name__)


class RepositorioContratosSQLAlchemy(RepositorioContratos):
    """Implementación SQLAlchemy del repositorio de contratos."""
    
    def __init__(self):
        # Sin parámetros, usa db.session directamente como en el tutorial
        pass
    
    def obtener_por_id(self, id: str) -> Optional[Contrato]:
        """Obtiene un contrato por ID."""
        logger.info(f"REPOSITORIO: Buscando contrato por ID: {id}")
        
        modelo = db.session.query(ContratoModelo).filter(
            ContratoModelo.id == id
        ).first()
        
        if modelo:
            logger.info(f"REPOSITORIO: Contrato encontrado: {modelo.influencer_nombre} - {modelo.campana_nombre}")
            return ContratoMapper.a_entidad(modelo)
        
        logger.info(f"REPOSITORIO: Contrato no encontrado: {id}")
        return None
    
    def obtener_por_influencer(self, influencer_id: str) -> List[Contrato]:
        """Obtiene contratos por ID de influencer."""
        logger.info(f"REPOSITORIO: Buscando contratos por influencer: {influencer_id}")
        
        modelos = db.session.query(ContratoModelo).filter(
            ContratoModelo.influencer_id == influencer_id
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados para influencer {influencer_id}")
        return contratos
    
    def obtener_por_campana(self, campana_id: str) -> List[Contrato]:
        """Obtiene contratos por ID de campaña."""
        logger.info(f"REPOSITORIO: Buscando contratos por campaña: {campana_id}")
        
        modelos = db.session.query(ContratoModelo).filter(
            ContratoModelo.campana_id == campana_id
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados para campaña {campana_id}")
        return contratos
    
    def agregar(self, entidad: Contrato) -> None:
        """Agrega un contrato."""
        logger.info(f"REPOSITORIO: Agregando contrato - ID: {entidad.id}")
        logger.info(f"REPOSITORIO: Influencer: {entidad.influencer.nombre}, Campaña: {entidad.campana.nombre}")
        
        modelo = ContratoMapper.a_modelo(entidad)
        logger.info(f"REPOSITORIO: Modelo SQLAlchemy creado - ID: {modelo.id}")
        
        db.session.add(modelo)
        logger.info(f"REPOSITORIO: Contrato agregado a la sesión - ID: {modelo.id}")
        
        if modelo in db.session.new:
            logger.info(f"REPOSITORIO: Confirmado - El modelo está en session.new")
        else:
            logger.warning(f"REPOSITORIO: PROBLEMA - El modelo NO está en session.new")
    
    def actualizar(self, entidad: Contrato) -> None:
        """Actualiza un contrato."""
        logger.info(f"REPOSITORIO: Actualizando contrato - ID: {entidad.id}")
        
        modelo = db.session.query(ContratoModelo).filter(
            ContratoModelo.id == entidad.id
        ).first()
        
        if modelo:
            ContratoMapper.actualizar_modelo(modelo, entidad)
            logger.info(f"REPOSITORIO: Contrato actualizado - ID: {entidad.id}")
        else:
            logger.warning(f"REPOSITORIO: Contrato no encontrado para actualizar: {entidad.id}")
            raise ValueError(f"Contrato con ID {entidad.id} no encontrado")
    
    def eliminar(self, id: str) -> None:
        """Elimina un contrato."""
        logger.info(f"REPOSITORIO: Eliminando contrato - ID: {id}")
        
        modelo = db.session.query(ContratoModelo).filter(
            ContratoModelo.id == id
        ).first()
        
        if modelo:
            db.session.delete(modelo)
            logger.info(f"REPOSITORIO: Contrato eliminado - ID: {id}")
        else:
            logger.warning(f"REPOSITORIO: Contrato no encontrado para eliminar: {id}")
    
    def obtener_todos(self) -> List[Contrato]:
        """Obtiene todos los contratos."""
        logger.info("REPOSITORIO: Obteniendo todos los contratos")
        
        modelos = db.session.query(ContratoModelo).all()
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados")
        return contratos
    
    def obtener_por_estado(self, estado: EstadoContrato) -> List[Contrato]:
        """Obtiene contratos por estado."""
        logger.info(f"REPOSITORIO: Buscando contratos por estado: {estado.value}")
        
        modelos = db.session.query(ContratoModelo).filter(
            ContratoModelo.estado == estado.value
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados con estado {estado.value}")
        return contratos
    
    def obtener_por_tipo(self, tipo: TipoContrato) -> List[Contrato]:
        """Obtiene contratos por tipo."""
        logger.info(f"REPOSITORIO: Buscando contratos por tipo: {tipo.value}")
        
        modelos = db.session.query(ContratoModelo).filter(
            ContratoModelo.tipo_contrato == tipo.value
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados con tipo {tipo.value}")
        return contratos
    
    def obtener_por_categoria(self, categoria: str) -> List[Contrato]:
        """Obtiene contratos que incluyen una categoría específica."""
        logger.info(f"REPOSITORIO: Buscando contratos por categoría: {categoria}")
        
        # Buscar en el JSON de categorías
        modelos = db.session.query(ContratoModelo).filter(
            func.json_array_length(ContratoModelo.categorias) > 0
        ).all()
        
        # Filtrar en Python para búsqueda más precisa
        contratos_filtrados = []
        for modelo in modelos:
            if categoria.lower() in [cat.lower() for cat in modelo.categorias]:
                contratos_filtrados.append(ContratoMapper.a_entidad(modelo))
        
        logger.info(f"REPOSITORIO: {len(contratos_filtrados)} contratos encontrados con categoría {categoria}")
        return contratos_filtrados
    
    def obtener_vigentes(self) -> List[Contrato]:
        """Obtiene contratos vigentes."""
        logger.info("REPOSITORIO: Buscando contratos vigentes")
        
        ahora = datetime.now()
        modelos = db.session.query(ContratoModelo).filter(
            and_(
                ContratoModelo.estado == EstadoContrato.ACTIVO.value,
                ContratoModelo.fecha_inicio_contrato <= ahora,
                or_(
                    ContratoModelo.fecha_fin_contrato.is_(None),
                    ContratoModelo.fecha_fin_contrato >= ahora
                )
            )
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos vigentes encontrados")
        return contratos
    
    def obtener_por_rango_fechas(self, fecha_inicio: str, fecha_fin: str) -> List[Contrato]:
        """Obtiene contratos dentro de un rango de fechas."""
        logger.info(f"REPOSITORIO: Buscando contratos entre {fecha_inicio} y {fecha_fin}")
        
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
        fecha_fin_dt = datetime.fromisoformat(fecha_fin)
        
        modelos = db.session.query(ContratoModelo).filter(
            and_(
                ContratoModelo.fecha_inicio_contrato >= fecha_inicio_dt,
                or_(
                    ContratoModelo.fecha_fin_contrato.is_(None),
                    ContratoModelo.fecha_fin_contrato <= fecha_fin_dt
                )
            )
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados en rango de fechas")
        return contratos
    
    def obtener_por_monto_minimo(self, monto_minimo: float) -> List[Contrato]:
        """Obtiene contratos con monto mínimo."""
        logger.info(f"REPOSITORIO: Buscando contratos con monto >= {monto_minimo}")
        
        modelos = db.session.query(ContratoModelo).filter(
            ContratoModelo.monto_base >= monto_minimo
        ).all()
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados con monto >= {monto_minimo}")
        return contratos
    
    def existe_contrato_activo(self, influencer_id: str, campana_id: str) -> bool:
        """Verifica si existe un contrato activo entre influencer y campaña."""
        logger.info(f"REPOSITORIO: Verificando contrato activo entre {influencer_id} y {campana_id}")
        
        existe = db.session.query(ContratoModelo).filter(
            and_(
                ContratoModelo.influencer_id == influencer_id,
                ContratoModelo.campana_id == campana_id,
                ContratoModelo.estado == EstadoContrato.ACTIVO.value
            )
        ).first() is not None
        
        logger.info(f"REPOSITORIO: Contrato activo {'existe' if existe else 'no existe'}")
        return existe
    
    def obtener_con_filtros(self, 
                           estado: Optional[EstadoContrato] = None,
                           tipo: Optional[TipoContrato] = None,
                           categoria: Optional[str] = None,
                           influencer_id: Optional[str] = None,
                           campana_id: Optional[str] = None,
                           monto_minimo: Optional[float] = None,
                           monto_maximo: Optional[float] = None,
                           limite: int = 100,
                           offset: int = 0) -> List[Contrato]:
        """Obtiene contratos con múltiples filtros."""
        logger.info("REPOSITORIO: Aplicando filtros múltiples")
        
        query = db.session.query(ContratoModelo)
        
        # Aplicar filtros
        if estado:
            query = query.filter(ContratoModelo.estado == estado.value)
        
        if tipo:
            query = query.filter(ContratoModelo.tipo_contrato == tipo.value)
        
        if influencer_id:
            query = query.filter(ContratoModelo.influencer_id == influencer_id)
        
        if campana_id:
            query = query.filter(ContratoModelo.campana_id == campana_id)
        
        if monto_minimo is not None:
            query = query.filter(ContratoModelo.monto_base >= monto_minimo)
        
        if monto_maximo is not None:
            query = query.filter(ContratoModelo.monto_base <= monto_maximo)
        
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
        
        contratos = [ContratoMapper.a_entidad(modelo) for modelo in modelos]
        logger.info(f"REPOSITORIO: {len(contratos)} contratos encontrados con filtros aplicados")
        return contratos