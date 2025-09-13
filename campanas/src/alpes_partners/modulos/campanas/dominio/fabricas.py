""" Fábricas para la creación de objetos del dominio de campanas

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de campanas

"""

from dataclasses import dataclass
from typing import Any

# Importaciones usando el path correcto para el contexto de ejecución
import sys
import os

# Agregar el directorio src al path si no está
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from alpes_partners.seedwork.dominio.repositorios import Mapeador
from alpes_partners.seedwork.dominio.entidades import Entidad
from alpes_partners.modulos.campanas.aplicacion.dto import RegistrarCampanaDTO

from .entidades import Campana
from .excepciones import TipoObjetoNoExisteEnDominioCampanasExcepcion


@dataclass
class _FabricaCampana:
    """Fábrica interna para crear campanas."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if isinstance(obj, Entidad):
            # Convertir entidad a DTO
            return mapeador.entidad_a_dto(obj) if mapeador else obj
        else:
            # Crear entidad desde DTO
            if isinstance(obj, RegistrarCampanaDTO):
                from .objetos_valor import TipoComision
                
                campana = Campana.crear(
                    nombre=obj.nombre,
                    descripcion=obj.descripcion,
                    tipo_comision=TipoComision(obj.tipo_comision.lower()),
                    valor_comision=obj.valor_comision,
                    moneda=obj.moneda,
                    fecha_inicio=obj.fecha_inicio,
                    fecha_fin=obj.fecha_fin,
                    titulo_material=obj.titulo_material,
                    descripcion_material=obj.descripcion_material,
                    categorias_objetivo=obj.categorias_objetivo,
                    tipos_afiliado_permitidos=obj.tipos_afiliado_permitidos
                )
                
                # Agregar material promocional si está presente
                if obj.enlaces_material or obj.imagenes_material or obj.banners_material:
                    from .objetos_valor import MaterialPromocional
                    material_actualizado = MaterialPromocional(
                        titulo=campana.material_promocional.titulo,
                        descripcion=campana.material_promocional.descripcion,
                        enlaces=obj.enlaces_material or [],
                        imagenes=obj.imagenes_material or [],
                        banners=obj.banners_material or []
                    )
                    campana.material_promocional = material_actualizado
                
                # Agregar criterios adicionales si están presentes
                if obj.paises_permitidos or obj.metricas_minimas:
                    from .objetos_valor import CriteriosAfiliado
                    criterios_actualizados = CriteriosAfiliado(
                        tipos_permitidos=campana.criterios_afiliado.tipos_permitidos,
                        categorias_requeridas=campana.criterios_afiliado.categorias_requeridas,
                        paises_permitidos=obj.paises_permitidos or [],
                        metricas_minimas=obj.metricas_minimas or {}
                    )
                    campana.criterios_afiliado = criterios_actualizados
                
                # Auto-activar si es solicitado
                if obj.auto_activar:
                    try:
                        campana.activar()
                    except Exception:
                        pass  # Si no se puede activar, continuar sin activar
                
                return campana
            elif mapeador:
                return mapeador.dto_a_entidad(obj)
            else:
                return obj


@dataclass
class FabricaCampanas:
    """Fábrica principal para objetos del dominio de campanas."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if (isinstance(obj, RegistrarCampanaDTO) or 
            (mapeador and mapeador.obtener_tipo() == Campana.__class__)):
            fabrica_campana = _FabricaCampana()
            return fabrica_campana.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioCampanasExcepcion(f"No se puede crear objeto para el tipo: {type(obj)}")
