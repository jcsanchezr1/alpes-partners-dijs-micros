"""Fábricas para la creación de objetos en la capa de infraestructura del dominio de reportes

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos en la capa de infraestructura del dominio de reportes

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

from reportes.seedwork.dominio.repositorios import Repositorio
from reportes.modulos.reportes.dominio.repositorios import RepositorioReportes

from .repositorios import RepositorioReportesSQLAlchemy
from .excepciones import ExcepcionFabricaReportes


@dataclass
class FabricaRepositorioReportes:
    """Fábrica para crear repositorios de reportes."""
    
    def crear_objeto(self, obj: type, mapeador: Any = None) -> RepositorioReportesSQLAlchemy:
        if obj == RepositorioReportesSQLAlchemy.__class__:
            # Crear una instancia del repositorio SIN sesión (como en el tutorial)
            # El repositorio usará db.session directamente
            return RepositorioReportesSQLAlchemy()
        else:
            raise ExcepcionFabricaReportes(f"No se puede crear repositorio para el tipo: {obj}")
