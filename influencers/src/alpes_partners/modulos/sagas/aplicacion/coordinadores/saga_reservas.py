import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from pydispatch import dispatcher

from .....seedwork.aplicacion.comandos import Comando, ejecutar_commando
from .....seedwork.dominio.eventos import EventoDominio, EventoIntegracion

# Importar eventos de dominio (convertimos eventos de integración a dominio)
from ....influencers.dominio.eventos import InfluencerRegistrado

# Importar eventos y comandos locales (para evitar dependencias entre microservicios)
from ...dominio.eventos import CampanaCreada, ContratoCreado
from ..comandos.comandos_externos import RegistrarCampana, CrearContrato

# Importar repositorio para saga log
from ...infraestructura.repositorio_saga_log import RepositorioSagaLogSQLAlchemy
from ...dominio.entidades import SagaLog
from .....seedwork.infraestructura.uow import UnidadTrabajoPuerto

# Importar handlers para registrar comandos externos
from .. import handlers

logger = logging.getLogger(__name__)


class EventoDominioInfluencerRegistrado(EventoDominio):
    """Evento de dominio para influencer registrado (conversión desde integración)."""
    
    def __init__(self, evento_integracion: InfluencerRegistrado):
        super().__init__()
        self.influencer_id = evento_integracion.influencer_id
        self.nombre = evento_integracion.nombre
        self.email = evento_integracion.email
        self.categorias = evento_integracion.categorias
        self.plataformas = evento_integracion.plataformas
        self.fecha_registro = evento_integracion.fecha_registro


class EventoDominioCampanaCreada(EventoDominio):
    """Evento de dominio para campaña creada (conversión desde integración)."""
    
    def __init__(self, evento_integracion: CampanaCreada):
        super().__init__()
        self.campana_id = evento_integracion.campana_id
        self.nombre = evento_integracion.nombre
        self.descripcion = evento_integracion.descripcion
        self.tipo_comision = evento_integracion.tipo_comision
        self.valor_comision = evento_integracion.valor_comision
        self.moneda = evento_integracion.moneda
        self.categorias_objetivo = evento_integracion.categorias_objetivo
        self.fecha_inicio = evento_integracion.fecha_inicio
        self.fecha_fin = evento_integracion.fecha_fin
        self.influencer_id = evento_integracion.influencer_id
        self.influencer_nombre = evento_integracion.influencer_nombre
        self.influencer_email = evento_integracion.influencer_email


class EventoDominioContratoCreado(EventoDominio):
    """Evento de dominio para contrato creado (conversión desde integración)."""
    
    def __init__(self, evento_integracion: ContratoCreado):
        super().__init__()
        self.contrato_id = evento_integracion.contrato_id
        self.influencer_id = evento_integracion.influencer_id
        self.campana_id = evento_integracion.campana_id
        self.monto_total = evento_integracion.monto_total
        self.moneda = evento_integracion.moneda
        self.fecha_inicio = evento_integracion.fecha_inicio
        self.fecha_fin = evento_integracion.fecha_fin
        self.tipo_contrato = evento_integracion.tipo_contrato
        self.fecha_creacion = evento_integracion.fecha_creacion


class CoordinadorInfluencersCampanasContratos:
    """Coordinador de saga para orquestar influencers, campañas y contratos."""
    
    def __init__(self):
        self.id_correlacion = str(uuid.uuid4())
        self.repositorio_saga_log = RepositorioSagaLogSQLAlchemy()
        logger.info(f"SAGA: Iniciando coordinador con correlación: {self.id_correlacion}")
    
    def persistir_en_saga_log(self, evento: EventoDominio, comando: Comando = None, paso_index: int = None, estado: str = "pendiente"):
        """Persistir estado en DB usando el repositorio de saga log."""
        logger.info(f"SAGA: Persistiendo en log - Evento: {type(evento).__name__}")
        
        try:
            # Crear entrada del saga log
            saga_log = SagaLog(
                id_correlacion=self.id_correlacion,
                evento_tipo=type(evento).__name__,
                evento_datos=evento.to_dict() if hasattr(evento, 'to_dict') else {},
                comando_tipo=type(comando).__name__ if comando else None,
                comando_datos=comando.__dict__ if comando else None,
                paso_index=paso_index,
                estado=estado,
                fecha_procesamiento=datetime.utcnow()
            )
            
            # Usar el sistema de UoW para persistir
            UnidadTrabajoPuerto.registrar_batch(self.repositorio_saga_log.agregar, saga_log)
            UnidadTrabajoPuerto.savepoint()
            UnidadTrabajoPuerto.commit()
            
            logger.info(f"SAGA: Log persistido exitosamente - ID: {saga_log.id}")
            
        except Exception as e:
            logger.error(f"SAGA: Error al persistir log: {e}")
            raise
    
    def construir_comando(self, evento: EventoDominio, tipo_comando: type) -> Comando:
        """Construir comando basado en el evento de dominio."""
        logger.info(f"SAGA: Construyendo comando {tipo_comando.__name__} desde evento {type(evento).__name__}")
        
        try:
            if isinstance(evento, EventoDominioInfluencerRegistrado) and tipo_comando == RegistrarCampana:
                # Cuando un influencer se registra, crear una campaña automáticamente
                comando = RegistrarCampana(
                    fecha_creacion=datetime.utcnow().isoformat(),
                    fecha_actualizacion=datetime.utcnow().isoformat(),
                    id=str(uuid.uuid4()),
                    nombre=f"Campaña de bienvenida para {evento.nombre}",
                    descripcion=f"Campaña automática creada para el influencer {evento.nombre}",
                    tipo_comision="fijo",
                    valor_comision=100.0,
                    moneda="USD",
                    fecha_inicio=datetime.utcnow().isoformat(),
                    fecha_fin=None,
                    titulo_material="Material de bienvenida",
                    descripcion_material="Material promocional para nuevos influencers",
                    categorias_objetivo=evento.categorias,
                    tipos_afiliado_permitidos=["influencer"],
                    paises_permitidos=["CO", "MX", "AR"],
                    enlaces_material=[],
                    imagenes_material=[],
                    banners_material=[],
                    metricas_minimas={},
                    auto_activar=True,
                    influencer_origen_id=evento.influencer_id,
                    categoria_origen=evento.categorias[0] if evento.categorias else "general",
                    influencer_origen_nombre=evento.nombre,
                    influencer_origen_email=evento.email
                )
                logger.info(f"SAGA: Comando RegistrarCampana construido para influencer {evento.nombre}")
                return comando
                
            elif isinstance(evento, EventoDominioCampanaCreada) and tipo_comando == CrearContrato:
                # Cuando se crea una campaña, crear un contrato automáticamente
                comando = CrearContrato(
                    fecha_creacion=datetime.utcnow().isoformat(),
                    fecha_actualizacion=datetime.utcnow().isoformat(),
                    id=str(uuid.uuid4()),
                    influencer_id=evento.influencer_id,
                    influencer_nombre=evento.influencer_nombre,
                    influencer_email=evento.influencer_email,
                    campana_id=evento.campana_id,
                    campana_nombre=evento.nombre,
                    categorias=evento.categorias_objetivo or [],
                    descripcion=f"Contrato automático para la campaña: {evento.nombre}",
                    monto_base=evento.valor_comision,
                    moneda=evento.moneda,
                    fecha_inicio=evento.fecha_inicio.isoformat() if hasattr(evento.fecha_inicio, 'isoformat') else str(evento.fecha_inicio),
                    fecha_fin=evento.fecha_fin.isoformat() if evento.fecha_fin and hasattr(evento.fecha_fin, 'isoformat') else str(evento.fecha_fin) if evento.fecha_fin else None,
                    entregables="Contenido promocional según especificaciones de la campaña",
                    tipo_contrato="puntual"
                )
                logger.info(f"SAGA: Comando CrearContrato construido para campaña {evento.nombre}")
                return comando
            
            else:
                logger.warning(f"SAGA: No hay implementación para construir {tipo_comando.__name__} desde {type(evento).__name__}")
                raise NotImplementedError(f"No se puede construir comando {tipo_comando.__name__} desde evento {type(evento).__name__}")
                
        except Exception as e:
            logger.error(f"SAGA: Error al construir comando: {e}")
            raise
    
    def procesar_evento_influencer_registrado(self, evento: EventoDominioInfluencerRegistrado):
        """Procesar evento de influencer registrado."""
        logger.info(f"SAGA: Procesando InfluencerRegistrado para {evento.nombre}")
        
        try:
            # 1. Persistir el evento en el log
            self.persistir_en_saga_log(evento, paso_index=1, estado="procesando")
            
            # 2. Construir y ejecutar comando para crear campaña
            comando_campana = self.construir_comando(evento, RegistrarCampana)
            self.persistir_en_saga_log(evento, comando_campana, paso_index=1, estado="comando_creado")
            
            # 3. Ejecutar el comando
            ejecutar_commando(comando_campana)
            
            # 4. Marcar como completado
            self.persistir_en_saga_log(evento, comando_campana, paso_index=1, estado="completado")
            
            logger.info(f"SAGA: InfluencerRegistrado procesado exitosamente")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando InfluencerRegistrado: {e}")
            self.persistir_en_saga_log(evento, paso_index=1, estado="error")
            raise
    
    def procesar_evento_campana_creada(self, evento: EventoDominioCampanaCreada):
        """Procesar evento de campaña creada."""
        logger.info(f"SAGA: Procesando CampanaCreada para {evento.nombre}")
        
        try:
            # Solo crear contrato si hay información del influencer
            if not evento.influencer_id:
                logger.info(f"SAGA: CampanaCreada sin influencer asociado, saltando creación de contrato")
                self.persistir_en_saga_log(evento, paso_index=2, estado="saltado")
                return
            
            # 1. Persistir el evento en el log
            self.persistir_en_saga_log(evento, paso_index=2, estado="procesando")
            
            # 2. Construir y ejecutar comando para crear contrato
            comando_contrato = self.construir_comando(evento, CrearContrato)
            self.persistir_en_saga_log(evento, comando_contrato, paso_index=2, estado="comando_creado")
            
            # 3. Ejecutar el comando
            ejecutar_commando(comando_contrato)
            
            # 4. Marcar como completado
            self.persistir_en_saga_log(evento, comando_contrato, paso_index=2, estado="completado")
            
            logger.info(f"SAGA: CampanaCreada procesado exitosamente")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando CampanaCreada: {e}")
            self.persistir_en_saga_log(evento, paso_index=2, estado="error")
            raise
    
    def procesar_evento_contrato_creado(self, evento: EventoDominioContratoCreado):
        """Procesar evento de contrato creado."""
        logger.info(f"SAGA: Procesando ContratoCreado - ID: {evento.contrato_id}")
        
        try:
            # 1. Persistir el evento en el log (final de la saga)
            self.persistir_en_saga_log(evento, paso_index=3, estado="saga_completada")
            
            logger.info(f"SAGA: ContratoCreado procesado exitosamente - Saga completada")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando ContratoCreado: {e}")
            self.persistir_en_saga_log(evento, paso_index=3, estado="error")
            raise


# Función para convertir eventos de integración a eventos de dominio y procesarlos
def oir_mensaje(mensaje):
    """Escuchar eventos de integración y convertirlos a eventos de dominio."""
    logger.info(f"SAGA: Recibiendo mensaje de tipo: {type(mensaje).__name__}")
    
    try:
        coordinador = CoordinadorInfluencersCampanasContratos()
        
        if isinstance(mensaje, InfluencerRegistrado):
            evento_dominio = EventoDominioInfluencerRegistrado(mensaje)
            coordinador.procesar_evento_influencer_registrado(evento_dominio)
            
        elif isinstance(mensaje, CampanaCreada):
            evento_dominio = EventoDominioCampanaCreada(mensaje)
            coordinador.procesar_evento_campana_creada(evento_dominio)
            
        elif isinstance(mensaje, ContratoCreado):
            evento_dominio = EventoDominioContratoCreado(mensaje)
            coordinador.procesar_evento_contrato_creado(evento_dominio)
            
        else:
            logger.warning(f"SAGA: Tipo de evento no soportado: {type(mensaje).__name__}")
            raise NotImplementedError(f"El evento {type(mensaje).__name__} no es soportado por la saga")
            
    except Exception as e:
        logger.error(f"SAGA: Error procesando mensaje: {e}")
        raise


# Registrar handlers usando pydispatch (similar al patrón de vuelos)
logger.info("SAGA: Registrando handlers de eventos con pydispatch")

dispatcher.connect(
    lambda sender, **kwargs: oir_mensaje(kwargs.get('evento')), 
    signal=f'{InfluencerRegistrado.__name__}Integracion'
)

dispatcher.connect(
    lambda sender, **kwargs: oir_mensaje(kwargs.get('evento')), 
    signal=f'{CampanaCreada.__name__}Integracion'
)

dispatcher.connect(
    lambda sender, **kwargs: oir_mensaje(kwargs.get('evento')), 
    signal=f'{ContratoCreado.__name__}Integracion'
)

logger.info("SAGA: Handlers registrados exitosamente")
