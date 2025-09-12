from datetime import datetime
from typing import List, Optional, Dict, Any
from alpes_partners.seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass


class CrearReporte(Comando):
    """Comando para crear un nuevo reporte."""
    def __init__(self,
                 nombre: str,
                 descripcion: str,
                 tipo_reporte: str,  # 'campana', 'contrato', 'general'
                 datos_origen: Dict[str, Any],
                 origen_evento: str,
                 estado: str = "activo",  # Campo para manejo de compensación
                 version_esquema: str = "1.0",
                 datos_adicionales: Optional[Dict[str, Any]] = None,
                 incluir_metricas: bool = True,
                 formato_salida: str = "json",
                 notificar_completado: bool = False,
                 campana_origen_id: Optional[str] = None,
                 contrato_origen_id: Optional[str] = None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_reporte = tipo_reporte
        self.datos_origen = datos_origen
        self.origen_evento = origen_evento
        self.estado = estado  # Campo para compensación (activo, cancelado, procesando, completado)
        self.version_esquema = version_esquema
        self.datos_adicionales = datos_adicionales or {}
        self.incluir_metricas = incluir_metricas
        self.formato_salida = formato_salida
        self.notificar_completado = notificar_completado
        self.campana_origen_id = campana_origen_id
        self.contrato_origen_id = contrato_origen_id


