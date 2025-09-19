""" Fábricas para la creación de objetos en la capa de infrastructura del dominio de influencers

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos en la capa de infraestructura del dominio de influencers

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

from alpes_partners.seedwork.dominio.repositorios import Repositorio
from alpes_partners.modulos.influencers.dominio.repositorios import RepositorioInfluencers

from .repositorio_sqlalchemy import RepositorioInfluencersSQLAlchemy
from .excepciones import ExcepcionFabricaInfluencers


@dataclass
class FabricaRepositorioInfluencers:
    """Fábrica para crear repositorios de influencers."""
    
    def crear_objeto(self, obj: type, mapeador: Any = None) -> RepositorioInfluencersSQLAlchemy:
        if obj == RepositorioInfluencersSQLAlchemy:
            # Crear una instancia del repositorio SIN sesión (como en el tutorial)
            # El repositorio usará db.session directamente
            return RepositorioInfluencersSQLAlchemy()
        else:
            raise ExcepcionFabricaInfluencers(f"No se puede crear repositorio para el tipo: {obj}")
