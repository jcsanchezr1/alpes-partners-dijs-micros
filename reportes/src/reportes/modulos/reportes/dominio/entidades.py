from datetime import datetime
from typing import Optional, Dict, Any

from reportes.seedwork.dominio.entidades import AgregacionRaiz
from reportes.seedwork.dominio.excepciones import ExcepcionReglaDeNegocio, ExcepcionEstadoInvalido

from .objetos_valor import EstadoReporte, TipoReporte, MetadatosReporte, ConfiguracionReporte
from .eventos import ReporteCreado


class Reporte(AgregacionRaiz):
    """Agregado raíz para Reporte."""
    
    def __init__(self,
                 nombre: str,
                 descripcion: str,
                 tipo_reporte: TipoReporte,
                 datos_origen: Dict[str, Any],
                 metadatos: MetadatosReporte,
                 configuracion: ConfiguracionReporte = None,
                 id: Optional[str] = None):
        super().__init__(id)
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.tipo_reporte = tipo_reporte
        self.datos_origen = datos_origen
        self.metadatos = metadatos
        self.configuracion = configuracion or ConfiguracionReporte()
        self.estado = EstadoReporte.ACTIVO
        
        # Validaciones
        if not self.nombre:
            raise ExcepcionReglaDeNegocio("El nombre del reporte es requerido")
        
        if not self.descripcion:
            raise ExcepcionReglaDeNegocio("La descripción del reporte es requerida")
        
        if not self.datos_origen:
            raise ExcepcionReglaDeNegocio("Los datos de origen son requeridos")
        
        # Emitir evento de creación
        self.agregar_evento(ReporteCreado(
            reporte_id=self.id,
            nombre=self.nombre,
            descripcion=self.descripcion,
            tipo_reporte=self.tipo_reporte,
            datos_origen=self.datos_origen,
            origen_evento=self.metadatos.origen_evento
        ))
    
    @classmethod
    def crear(cls, 
              nombre: str,
              descripcion: str,
              tipo_reporte: TipoReporte,
              datos_origen: Dict[str, Any],
              origen_evento: str,
              version_esquema: str = "1.0",
              datos_adicionales: Optional[Dict[str, Any]] = None) -> 'Reporte':
        """Factory method para crear un reporte."""
        
        # Crear objetos valor
        metadatos = MetadatosReporte(
            origen_evento=origen_evento,
            version_esquema=version_esquema,
            datos_adicionales=datos_adicionales or {}
        )
        
        configuracion = ConfiguracionReporte(
            incluir_metricas=True,
            formato_salida="json",
            notificar_completado=False
        )
        
        return cls(
            nombre=nombre,
            descripcion=descripcion,
            tipo_reporte=tipo_reporte,
            datos_origen=datos_origen,
            metadatos=metadatos,
            configuracion=configuracion
        )
    
    def crear_reporte(self, reporte: 'Reporte') -> None:
        """Método para crear el reporte y emitir el evento correspondiente."""
        # Emitir evento de creación
        from .eventos import ReporteCreado
        self.agregar_evento(ReporteCreado(
            reporte_id=self.id,
            nombre=self.nombre,
            descripcion=self.descripcion,
            tipo_reporte=self.tipo_reporte,
            datos_origen=self.datos_origen,
            origen_evento=self.metadatos.origen_evento
        ))
