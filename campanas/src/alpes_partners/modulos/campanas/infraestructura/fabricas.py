""" Fábricas para la creación de objetos en la capa de infrastructura del dominio de campanas

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos en la capa de infraestructura del dominio de campanas

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
from alpes_partners.modulos.campanas.dominio.repositorios import RepositorioCampanas

from .repositorios import RepositorioCampanasSQLAlchemy
from .excepciones import ExcepcionFabricaCampanas


@dataclass
class FabricaRepositorioCampanas:
    """Fábrica para crear repositorios de campanas."""
    
    def crear_objeto(self, obj: type, mapeador: Any = None) -> RepositorioCampanasSQLAlchemy:
        if obj == RepositorioCampanasSQLAlchemy:
            # Crear una instancia del repositorio SIN sesión (como en el tutorial)
            # El repositorio usará db.session directamente
            return RepositorioCampanasSQLAlchemy()
        else:
            raise ExcepcionFabricaCampanas(f"No se puede crear repositorio para el tipo: {obj}")
