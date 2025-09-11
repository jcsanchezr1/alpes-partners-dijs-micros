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
from alpes_partners.modulos.contratos.aplicacion.dto import CrearContratoDTO

from .entidades import Contrato
from .excepciones import TipoObjetoNoExisteEnDominioContratosExcepcion

@dataclass
class _FabricaContrato:
    """Fábrica interna para crear contratos."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if isinstance(obj, Entidad):
            # Convertir entidad a DTO
            return mapeador.entidad_a_dto(obj) if mapeador else obj
        else:
            # Crear entidad desde DTO
            if isinstance(obj, CrearContratoDTO):
                from ..dominio.objetos_valor import TipoContrato
                from datetime import datetime
                
                # Determinar tipo de contrato
                try:
                    tipo_contrato = TipoContrato(obj.tipo_contrato)
                except ValueError:
                    tipo_contrato = TipoContrato.PUNTUAL
                
                contrato = Contrato.crear(
                    influencer_id=obj.influencer_id,
                    influencer_nombre=obj.influencer_nombre,
                    influencer_email=obj.influencer_email,
                    campana_id=obj.campana_id,
                    campana_nombre=obj.campana_nombre,
                    categorias=obj.categorias,
                    descripcion=obj.descripcion,
                    monto_base=obj.monto_base,
                    moneda=obj.moneda,
                    fecha_inicio=datetime.fromisoformat(obj.fecha_inicio),
                    fecha_fin=datetime.fromisoformat(obj.fecha_fin) if obj.fecha_fin else None,
                    entregables=obj.entregables or "",
                    tipo_contrato=tipo_contrato
                )
                return contrato
            elif mapeador:
                return mapeador.dto_a_entidad(obj)
            else:
                return obj


@dataclass
class FabricaContratos:
    """Fábrica principal para objetos del dominio de contratos."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if (isinstance(obj, CrearContratoDTO) or 
            (mapeador and mapeador.obtener_tipo() == Contrato.__class__)):
            fabrica_contrato = _FabricaContrato()
            return fabrica_contrato.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioContratosExcepcion(f"No se puede crear objeto para el tipo: {type(obj)}")
