import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass
from pydispatch import dispatcher

from .....seedwork.aplicacion.comandos import Comando, ejecutar_commando
from .....seedwork.dominio.eventos import EventoDominio, EventoIntegracion

# Importar eventos de dominio (convertimos eventos de integración a dominio)
from ....influencers.dominio.eventos import InfluencerRegistrado

# Importar eventos y comandos locales (para evitar dependencias entre microservicios)
from ...dominio.eventos import CampanaCreada, ContratoCreado, ErrorCreacionCampana, ErrorCreacionContrato, CompensacionEjecutada
from ..comandos.comandos_externos import RegistrarCampana, CrearContrato, EliminarCampana

# Importar clases base para saga
from .....seedwork.aplicacion.sagas import CoordinadorOrquestacion, Transaccion, Inicio, Fin

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


# Eventos de error para la saga - ahora importados desde dominio.eventos


# Comandos de compensación
@dataclass
class EliminarContrato(Comando):
    """Comando para eliminar un contrato (compensación)."""
    contrato_id: str
    campana_id: str
    razon: str = "Compensación por falla en saga"


class CoordinadorInfluencersCampanasContratos(CoordinadorOrquestacion):
    """Coordinador de saga para orquestar influencers, campañas y contratos."""
    
    # Instancia singleton
    _instancia = None
    _id_correlacion_global = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            # Inicializar solo una vez cuando se crea la instancia
            cls._instancia._inicializado = False
        return cls._instancia
    
    def __init__(self):
        # Solo inicializar una vez
        if hasattr(self, '_inicializado') and self._inicializado:
            return
            
        # Usar el mismo id_correlacion para toda la saga
        if CoordinadorInfluencersCampanasContratos._id_correlacion_global is None:
            CoordinadorInfluencersCampanasContratos._id_correlacion_global = str(uuid.uuid4())
        
        self.id_correlacion = CoordinadorInfluencersCampanasContratos._id_correlacion_global
        self.repositorio_saga_log = RepositorioSagaLogSQLAlchemy()
        self.pasos = []
        self.index = 0
        # Contexto de la saga para compensación
        self.contexto_influencer = None
        self.contexto_campana = None
        self.inicializar_pasos()
        self._inicializado = True
        logger.info(f"SAGA: Iniciando coordinador con correlación: {self.id_correlacion}")
    
    def inicializar_pasos(self):
        """Inicializar los pasos de la saga con influencers, campañas y contratos."""
        self.pasos = [
            Inicio(index=0),
            Transaccion(
                index=1, 
                comando=RegistrarCampana, 
                evento=EventoDominioCampanaCreada, 
                error=ErrorCreacionCampana, 
                compensacion=EliminarCampana
            ),
            Transaccion(
                index=2, 
                comando=CrearContrato, 
                evento=EventoDominioContratoCreado, 
                error=ErrorCreacionContrato, 
                compensacion=EliminarContrato
            ),
            Fin(index=3)
        ]
    
    @classmethod
    def reset_correlacion(cls):
        """Resetear el id_correlacion para una nueva saga."""
        cls._id_correlacion_global = None
    
    def iniciar(self):
        """Iniciar la saga."""
        self.persistir_en_saga_log(self.pasos[0])
        logger.info(f"SAGA: Saga iniciada con correlación: {self.id_correlacion}")
    
    def terminar(self):
        """Terminar la saga."""
        self.persistir_en_saga_log(self.pasos[-1])
        logger.info(f"SAGA: Saga terminada con correlación: {self.id_correlacion}")
    
    def terminar_con_error(self, error: str):
        """Terminar la saga con error."""
        logger.error(f"SAGA: Saga terminada con error: {error}")
        logger.error(f"SAGA: Correlación: {self.id_correlacion}")
        # Aquí podrías persistir el estado de error en el log si es necesario
    
    def persistir_en_saga_log(self, evento, paso_index: int = None):
        """Persistir evento en DB usando el repositorio de saga log (un registro por evento)."""
        logger.info(f"SAGA: Persistiendo en log - Evento: {type(evento).__name__}")
        
        try:
            # Verificar si ya existe un registro para este evento en esta correlación
            entradas_existentes = self.repositorio_saga_log.obtener_por_correlacion(self.id_correlacion)
            
            # Buscar si ya existe un registro para este tipo de evento
            evento_ya_registrado = any(
                entrada.evento_tipo == type(evento).__name__ and 
                entrada.paso_index == paso_index
                for entrada in entradas_existentes
            )
            
            if evento_ya_registrado:
                logger.info(f"SAGA: Evento {type(evento).__name__} ya registrado, saltando duplicado")
                return
            
            # Preparar datos del evento
            if hasattr(evento, 'to_dict'):
                evento_datos = evento.to_dict()
            elif isinstance(evento, dict):
                evento_datos = evento
            else:
                evento_datos = {}
            
            # Crear entrada del saga log
            saga_log = SagaLog(
                id_correlacion=self.id_correlacion,
                evento_tipo=type(evento).__name__,
                evento_datos=evento_datos,
                paso_index=paso_index,
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
                    tipo_comision="cpa",
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
            
            # Comandos de compensación
            elif isinstance(evento, ErrorCreacionContrato) and tipo_comando == EliminarCampana:
                # Si falla la creación del contrato, eliminar la campaña
                logger.info(f"SAGA: DEBUG - Contexto influencer: {self.contexto_influencer}")
                influencer_id = self.contexto_influencer.get('influencer_id', '') if self.contexto_influencer else ''
                
                # Si no tenemos el influencer_id del contexto, intentar obtenerlo del saga log
                if not influencer_id:
                    logger.warning(f"SAGA: No se encontró influencer_id en contexto, buscando en saga log")
                    entradas_existentes = self.repositorio_saga_log.obtener_por_correlacion(self.id_correlacion)
                    for entrada in entradas_existentes:
                        if entrada.evento_tipo == 'EventoDominioInfluencerRegistrado':
                            datos = entrada.evento_datos
                            if isinstance(datos, dict) and 'influencer_id' in datos:
                                influencer_id = datos['influencer_id']
                                logger.info(f"SAGA: Influencer_id encontrado en saga log: {influencer_id}")
                                break
                
                # Si aún no tenemos influencer_id, usar None (opcional para compensación)
                if not influencer_id:
                    logger.warning(f"SAGA: No se pudo obtener influencer_id, procediendo sin él")
                    influencer_id = None
                
                comando = EliminarCampana(
                    campana_id=evento.campana_id,
                    influencer_id=influencer_id,
                    razon=f"Compensación por error en creación de contrato: {evento.error}"
                )
                logger.info(f"SAGA: Comando EliminarCampana construido para compensación - Campaña: {evento.campana_id}, Influencer: {influencer_id or 'N/A'}")
                return comando
            
            elif isinstance(evento, ErrorCreacionCampana) and tipo_comando == EliminarContrato:
                # Si falla la creación de campaña, no hay contrato que eliminar
                logger.info(f"SAGA: No se requiere compensación para error de campaña")
                return None
            
            else:
                logger.warning(f"SAGA: No hay implementación para construir {tipo_comando.__name__} desde {type(evento).__name__}")
                raise NotImplementedError(f"No se puede construir comando {tipo_comando.__name__} desde evento {type(evento).__name__}")
                
        except Exception as e:
            logger.error(f"SAGA: Error al construir comando: {e}")
            raise
    
    def procesar_evento_influencer_registrado(self, evento: EventoDominioInfluencerRegistrado):
        """Procesar evento de influencer registrado - inicio de la saga."""
        logger.info(f"SAGA: Procesando InfluencerRegistrado para {evento.nombre}")
        
        try:
            # Guardar contexto del influencer para compensación
            self.contexto_influencer = {
                'influencer_id': evento.influencer_id,
                'nombre': evento.nombre,
                'email': evento.email
            }
            
            # Iniciar la saga
            self.iniciar()
            
            # 1. Persistir el evento en el log
            self.persistir_en_saga_log(evento, paso_index=1)
            
            # 2. Construir y ejecutar comando para crear campaña
            comando_campana = self.construir_comando(evento, RegistrarCampana)
            
            # 3. Ejecutar el comando
            ejecutar_commando(comando_campana)
            
            logger.info(f"SAGA: InfluencerRegistrado procesado exitosamente")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando InfluencerRegistrado: {e}")
            raise
    
    def procesar_evento_campana_creada(self, evento: EventoDominioCampanaCreada):
        """Procesar evento de campaña creada - segundo paso de la saga."""
        logger.info(f"SAGA: Procesando CampanaCreada para {evento.nombre}")
        
        try:
            # Guardar contexto de la campaña para compensación
            self.contexto_campana = {
                'campana_id': evento.campana_id,
                'nombre': evento.nombre,
                'influencer_id': evento.influencer_id
            }
            
            # Solo crear contrato si hay información del influencer
            if not evento.influencer_id:
                logger.info(f"SAGA: CampanaCreada sin influencer asociado, saltando creación de contrato")
                return
            
            # 1. Persistir el evento en el log
            self.persistir_en_saga_log(evento, paso_index=2)
            
            # 2. Construir y ejecutar comando para crear contrato
            comando_contrato = self.construir_comando(evento, CrearContrato)
            
            # 3. Ejecutar el comando (envía evento al microservicio de contratos)
            ejecutar_commando(comando_contrato)
            
            # 4. NO marcar como exitoso aquí - esperar respuesta del microservicio de contratos
            logger.info(f"SAGA: Comando CrearContrato enviado - esperando respuesta del microservicio de contratos")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando CampanaCreada: {e}")
            raise
    
    def procesar_evento_contrato_creado(self, evento: EventoDominioContratoCreado):
        """Procesar evento de contrato creado - final de la saga."""
        logger.info(f"SAGA: Procesando ContratoCreado - ID: {evento.contrato_id}")
        
        try:
            # 1. Persistir el evento en el log (final de la saga)
            self.persistir_en_saga_log(evento, paso_index=3)
            
            # 2. Terminar la saga
            self.terminar()
            
            logger.info(f"SAGA: ContratoCreado procesado exitosamente - Saga completada")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando ContratoCreado: {e}")
            raise
    
    def procesar_evento_error_contrato(self, evento: ErrorCreacionContrato):
        """Procesar evento de error de contrato - iniciar compensación."""
        logger.error(f"SAGA: Procesando ErrorCreacionContrato - Campaña: {evento.campana_id}, Error: {evento.error}")
        
        try:
            # 1. Persistir el evento de error en el log
            self.persistir_en_saga_log(evento, paso_index=2)
            
            # 2. Iniciar compensación - eliminar la campaña creada
            logger.info(f"SAGA: Iniciando compensación - eliminando campaña {evento.campana_id}")
            
            # Construir comando de compensación
            comando_compensacion = self.construir_comando(evento, EliminarCampana)
            
            if comando_compensacion:
                # Persistir el comando de compensación en el log
                self.persistir_en_saga_log(comando_compensacion, paso_index=3)
                
                # Ejecutar compensación
                ejecutar_commando(comando_compensacion)
                logger.info(f"SAGA: Compensación ejecutada exitosamente - Campaña eliminada")
                
                # Persistir evento de compensación ejecutada
                evento_compensacion_ejecutada = CompensacionEjecutada(
                    comando='EliminarCampana',
                    campana_id=evento.campana_id,
                    influencer_id=comando_compensacion.influencer_id,
                    razon=comando_compensacion.razon,
                    fecha_ejecucion=datetime.utcnow()
                )
                self.persistir_en_saga_log(evento_compensacion_ejecutada, paso_index=4)
                
            else:
                logger.warning(f"SAGA: No se pudo construir comando de compensación")
            
            # 3. Marcar saga como fallida
            self.terminar_con_error(f"Error en creación de contrato: {evento.error}")
            
            logger.error(f"SAGA: ErrorCreacionContrato procesado - Compensación ejecutada")
            
        except Exception as e:
            logger.error(f"SAGA: Error procesando ErrorCreacionContrato: {e}")
            raise


# Función para convertir eventos de integración a eventos de dominio y procesarlos
def oir_mensaje(mensaje):
    """Escuchar eventos de integración y convertirlos a eventos de dominio."""
    logger.info(f"SAGA: Recibiendo mensaje de tipo: {type(mensaje).__name__}")
    
    try:
        # Si es el primer evento de la saga (InfluencerRegistrado), resetear correlación
        if isinstance(mensaje, InfluencerRegistrado):
            CoordinadorInfluencersCampanasContratos.reset_correlacion()
        
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
            
        elif isinstance(mensaje, ErrorCreacionContrato):
            logger.error(f"SAGA: Procesando evento de error de contrato - Campaña: {mensaje.campana_id}, Error: {mensaje.error}")
            logger.error(f"SAGA: Tipo de mensaje: {type(mensaje).__name__}")
            coordinador.procesar_evento_error_contrato(mensaje)
            
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
