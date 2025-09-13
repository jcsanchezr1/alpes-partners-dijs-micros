""" Mapeadores para la conversión de objetos en la capa de aplicación del dominio de campanas

En este archivo usted encontrará los diferentes mapeadores para convertir
objetos entre DTOs y entidades del dominio de campanas

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
from alpes_partners.modulos.campanas.dominio.entidades import Campana
from alpes_partners.modulos.campanas.aplicacion.dto import RegistrarCampanaDTO, CampanaDTO

from datetime import datetime


class MapeadorCampana(Mapeador):
    """Mapeador para convertir entre DTOs y Campanas."""
    
    def obtener_tipo(self) -> type:
        return Campana.__class__
    
    def entidad_a_dto(self, entidad: Campana) -> CampanaDTO:
        """Convierte una entidad Campana a DTO."""
        
        return CampanaDTO(
            id=entidad.id,
            nombre=entidad.nombre,
            descripcion=entidad.descripcion,
            estado=entidad.estado.value,
            tipo_comision=entidad.tipo_comision.value,
            valor_comision=entidad.valor_comision,
            moneda=entidad.moneda,
            fecha_inicio=entidad.fecha_inicio.isoformat() if isinstance(entidad.fecha_inicio, datetime) else entidad.fecha_inicio,
            fecha_fin=entidad.fecha_fin.isoformat() if entidad.fecha_fin and isinstance(entidad.fecha_fin, datetime) else entidad.fecha_fin,
            fecha_creacion=entidad.fecha_creacion.isoformat(),
            fecha_activacion=entidad.fecha_activacion.isoformat() if entidad.fecha_activacion else None,
            
            # Material promocional
            titulo_material=entidad.material_promocional.titulo,
            descripcion_material=entidad.material_promocional.descripcion,
            enlaces_material=entidad.material_promocional.enlaces,
            imagenes_material=entidad.material_promocional.imagenes,
            banners_material=entidad.material_promocional.banners,
            
            # Criterios de afiliado
            categorias_objetivo=entidad.criterios_afiliado.categorias_requeridas,
            tipos_afiliado_permitidos=entidad.criterios_afiliado.tipos_permitidos,
            paises_permitidos=entidad.criterios_afiliado.paises_permitidos,
            metricas_minimas=entidad.criterios_afiliado.metricas_minimas,
            
            # Métricas (por defecto 0 si no están disponibles)
            afiliados_activos=getattr(entidad, 'afiliados_activos', 0),
            conversiones_totales=getattr(entidad, 'conversiones_totales', 0),
            ingresos_generados=getattr(entidad, 'ingresos_generados', 0.0),
            
            # Origen
            influencer_origen_id=getattr(entidad, 'influencer_origen_id', None),
            categoria_origen=getattr(entidad, 'categoria_origen', None)
        )
    
    def dto_a_entidad(self, dto: RegistrarCampanaDTO) -> Campana:
        """Convierte un DTO a entidad Campana."""
        
        from alpes_partners.modulos.campanas.dominio.objetos_valor import TipoComision
        
        # Crear campana usando el método de fábrica de la entidad
        campana = Campana.crear(
            nombre=dto.nombre,
            descripcion=dto.descripcion,
            tipo_comision=TipoComision(dto.tipo_comision.lower()),
            valor_comision=dto.valor_comision,
            moneda=dto.moneda,
            fecha_inicio=datetime.fromisoformat(dto.fecha_inicio) if isinstance(dto.fecha_inicio, str) else dto.fecha_inicio,
            fecha_fin=datetime.fromisoformat(dto.fecha_fin) if dto.fecha_fin and isinstance(dto.fecha_fin, str) else dto.fecha_fin,
            titulo_material=dto.titulo_material,
            descripcion_material=dto.descripcion_material,
            categorias_objetivo=dto.categorias_objetivo,
            tipos_afiliado_permitidos=dto.tipos_afiliado_permitidos
        )
        
        # Agregar material promocional adicional si está presente
        if dto.enlaces_material or dto.imagenes_material or dto.banners_material:
            from alpes_partners.modulos.campanas.dominio.objetos_valor import MaterialPromocional
            material_actualizado = MaterialPromocional(
                titulo=campana.material_promocional.titulo,
                descripcion=campana.material_promocional.descripcion,
                enlaces=dto.enlaces_material or [],
                imagenes=dto.imagenes_material or [],
                banners=dto.banners_material or []
            )
            campana.material_promocional = material_actualizado
        
        # Agregar criterios adicionales si están presentes
        if dto.paises_permitidos or dto.metricas_minimas:
            from alpes_partners.modulos.campanas.dominio.objetos_valor import CriteriosAfiliado
            criterios_actualizados = CriteriosAfiliado(
                tipos_permitidos=campana.criterios_afiliado.tipos_permitidos,
                categorias_requeridas=campana.criterios_afiliado.categorias_requeridas,
                paises_permitidos=dto.paises_permitidos or [],
                metricas_minimas=dto.metricas_minimas or {}
            )
            campana.criterios_afiliado = criterios_actualizados
        
        # Establecer el ID si viene en el DTO (para comandos)
        if hasattr(dto, 'id') and dto.id:
            campana._id = dto.id
        
        # Auto-activar si es solicitado
        if dto.auto_activar:
            try:
                campana.activar()
            except Exception:
                pass  # Si no se puede activar, continuar sin activar
        
        # Asignar datos del influencer origen para eventos
        if hasattr(dto, 'influencer_origen_id'):
            campana.influencer_origen_id = dto.influencer_origen_id
        if hasattr(dto, 'influencer_origen_nombre'):
            campana.influencer_origen_nombre = dto.influencer_origen_nombre
        if hasattr(dto, 'influencer_origen_email'):
            campana.influencer_origen_email = dto.influencer_origen_email
        if hasattr(dto, 'categoria_origen'):
            campana.categoria_origen = dto.categoria_origen
        
        return campana
