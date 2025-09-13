""" Fábricas para la creación de objetos del dominio de influencers

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de influencers

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
from alpes_partners.modulos.influencers.aplicacion.dto import RegistrarInfluencerDTO

from .entidades import Influencer
from .excepciones import TipoObjetoNoExisteEnDominioInfluencersExcepcion


@dataclass
class _FabricaInfluencer:
    """Fábrica interna para crear influencers."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if isinstance(obj, Entidad):
            # Convertir entidad a DTO
            return mapeador.entidad_a_dto(obj) if mapeador else obj
        else:
            # Crear entidad desde DTO
            if isinstance(obj, RegistrarInfluencerDTO):
                influencer = Influencer.crear(
                    nombre=obj.nombre,
                    email=obj.email,
                    categorias=obj.categorias,
                    descripcion=obj.descripcion,
                    biografia=obj.biografia,
                    sitio_web=obj.sitio_web,
                    telefono=obj.telefono
                )
                return influencer
            elif mapeador:
                return mapeador.dto_a_entidad(obj)
            else:
                return obj


@dataclass
class FabricaInfluencers:
    """Fábrica principal para objetos del dominio de influencers."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if (isinstance(obj, RegistrarInfluencerDTO) or 
            (mapeador and mapeador.obtener_tipo() == Influencer.__class__)):
            fabrica_influencer = _FabricaInfluencer()
            return fabrica_influencer.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioInfluencersExcepcion(f"No se puede crear objeto para el tipo: {type(obj)}")
