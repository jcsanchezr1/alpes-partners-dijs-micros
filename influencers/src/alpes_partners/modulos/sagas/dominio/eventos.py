"""
Eventos de dominio locales para la saga.
Estos eventos representan eventos de otros microservicios pero definidos localmente
para evitar dependencias directas entre microservicios.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from ....seedwork.dominio.eventos import EventoDominio, EventoIntegracion


class CampanaCreada(EventoIntegracion):
    """Evento local que representa cuando se crea una campaña (desde microservicio campanas)."""
    
    def __init__(self, 
                 campana_id: str,
                 nombre: str,
                 descripcion: str,
                 tipo_comision: str,
                 valor_comision: float,
                 moneda: str,
                 categorias_objetivo: List[str],
                 fecha_inicio: datetime,
                 fecha_fin: datetime = None,
                 influencer_id: str = None,
                 influencer_nombre: str = None,
                 influencer_email: str = None):
        super().__init__()
        self.campana_id = campana_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_comision = tipo_comision
        self.valor_comision = valor_comision
        self.moneda = moneda
        self.categorias_objetivo = categorias_objetivo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.influencer_id = influencer_id
        self.influencer_nombre = influencer_nombre
        self.influencer_email = influencer_email


class ContratoCreado(EventoIntegracion):
    """Evento local que representa cuando se crea un contrato (desde microservicio contratos)."""
    
    def __init__(self, 
                 contrato_id: str,
                 influencer_id: str,
                 campana_id: str,
                 monto_total: float,
                 moneda: str,
                 fecha_inicio: datetime,
                 fecha_fin: datetime,
                 tipo_contrato: str,
                 fecha_creacion: datetime):
        super().__init__()
        self.contrato_id = contrato_id
        self.influencer_id = influencer_id
        self.campana_id = campana_id
        self.monto_total = monto_total
        self.moneda = moneda
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tipo_contrato = tipo_contrato
        self.fecha_creacion = fecha_creacion


class ErrorCreacionCampana(EventoDominio):
    """Evento de error cuando falla la creación de campaña."""
    
    def __init__(self, influencer_id: str, error: str):
        super().__init__()
        self.influencer_id = influencer_id
        self.error = error


class ErrorCreacionContrato(EventoDominio):
    """Evento de error cuando falla la creación de contrato."""
    
    def __init__(self, campana_id: str, error: str):
        super().__init__()
        self.campana_id = campana_id
        self.error = error


class CompensacionEjecutada(EventoDominio):
    """Evento que indica que una compensación fue ejecutada exitosamente."""
    
    def __init__(self, comando: str, campana_id: str, influencer_id: str, razon: str, fecha_ejecucion: datetime):
        super().__init__()
        self.comando = comando
        self.campana_id = campana_id
        self.influencer_id = influencer_id
        self.razon = razon
        self.fecha_ejecucion = fecha_ejecucion


class CampanaEliminacionRequerida(EventoIntegracion):
    """Evento de integración para solicitar eliminación de campaña (compensación)."""
    
    def __init__(self, campana_id: str, influencer_id: str, razon: str):
        super().__init__()
        self.campana_id = campana_id
        self.influencer_id = influencer_id
        self.razon = razon
