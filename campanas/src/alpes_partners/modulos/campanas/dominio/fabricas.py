""" Fábricas para la creación de objetos del dominio de campanas

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de campanas

"""

from dataclasses import dataclass
from typing import Any
import logging

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
            # Crear entidad desde DTO usando mapeador si está disponible
            if mapeador:
                return mapeador.dto_a_entidad(obj)
            elif isinstance(obj, RegistrarCampanaDTO):
                # Fallback si no hay mapeador
                from .objetos_valor import TipoComision
                
                from datetime import datetime
                
                campana = Campana.crear(
                    nombre=obj.nombre,
                    descripcion=obj.descripcion,
                    tipo_comision=TipoComision(obj.tipo_comision.lower()),
                    valor_comision=obj.valor_comision,
                    moneda=obj.moneda,
                    fecha_inicio=datetime.fromisoformat(obj.fecha_inicio) if isinstance(obj.fecha_inicio, str) else obj.fecha_inicio,
                    fecha_fin=datetime.fromisoformat(obj.fecha_fin) if obj.fecha_fin and isinstance(obj.fecha_fin, str) else obj.fecha_fin,
                    titulo_material=obj.titulo_material,
                    descripcion_material=obj.descripcion_material,
                    categorias_objetivo=obj.categorias_objetivo,
                    tipos_afiliado_permitidos=obj.tipos_afiliado_permitidos
                )
                return campana
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
