"""Excepciones de la capa de infraestructura del módulo de influencers."""

# Importaciones usando el path correcto para el contexto de ejecución
import sys
import os

# Agregar el directorio src al path si no está
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from alpes_partners.seedwork.dominio.excepciones import ExcepcionDominio


class ExcepcionFabricaContratos(ExcepcionDominio):
    """Excepción lanzada cuando hay un error en la fábrica de contratos."""
    pass


class ExcepcionFabricaInfluencers(ExcepcionDominio):
    """Excepción lanzada cuando hay un error en la fábrica de influencers (compatibilidad)."""
    pass
