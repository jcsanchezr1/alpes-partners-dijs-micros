from datetime import datetime
from typing import List, Optional
from alpes_partners.seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass

class CrearCampana(Comando):
    """Comando para crear una nueva campana."""
    def __init__(self,
                 nombre: str,
                 descripcion: str,
                 tipo_comision: str,  # 'cpa', 'cpl', 'cpc'
                 valor_comision: float,
                 moneda: str,
                 fecha_inicio: datetime,
                 fecha_fin: Optional[datetime] = None,
                 titulo_material: str = "",
                 descripcion_material: str = "",
                 categorias_objetivo: List[str] = None,
                 tipos_afiliado_permitidos: List[str] = None,
                 paises_permitidos: List[str] = None,
                 enlaces_material: List[str] = None,
                 imagenes_material: List[str] = None,
                 banners_material: List[str] = None,
                 metricas_minimas: dict = None,
                 auto_activar: bool = False,
                 influencer_origen_id: Optional[str] = None,
                 categoria_origen: Optional[str] = None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_comision = tipo_comision
        self.valor_comision = valor_comision
        self.moneda = moneda
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.titulo_material = titulo_material
        self.descripcion_material = descripcion_material
        self.categorias_objetivo = categorias_objetivo or []
        self.tipos_afiliado_permitidos = tipos_afiliado_permitidos or []
        self.paises_permitidos = paises_permitidos or []
        self.enlaces_material = enlaces_material or []
        self.imagenes_material = imagenes_material or []
        self.banners_material = banners_material or []
        self.metricas_minimas = metricas_minimas or {}
        self.auto_activar = auto_activar
        self.influencer_origen_id = influencer_origen_id
        self.categoria_origen = categoria_origen

