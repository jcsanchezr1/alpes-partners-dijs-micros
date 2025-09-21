# Arquitectura de Microservicios - Alpes Partners

Este repositorio contiene la implementación de microservicios para Alpes Partners, siguiendo principios de Domain Driven Design (DDD) y arquitectura orientada a eventos.

## Estructura del Proyecto

```
alpes-partners-dijs-micros/
├── influencers/                  # Microservicio de Influencers
├── campanas/                     # Microservicio de Campañas
├── contratos/                    # Microservicio de Contratos
├── bff/                          # Microservicio BFF
├── scripts-despliegue-pulsar-vm-gcp/  # Scripts para despliegue de Pulsar
├── scripts-envio-eventos-pulsar/      # Scripts para envío de eventos
├── docker-compose.yml            # Orquestación completa de microservicios
└── README.md                     # Este archivo
```

## Microservicios

### 1. Influencers (`influencers/`)

**Puerto**: 8000  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Gestión y registro de influencers

**Características**:
- Arquitectura DDD con capas bien definidas
- Eventos de integración vía Apache Pulsar
- Genera eventos de `InfluencerRegistrado`

### 2. Campañas (`campanas/`)

**Puerto**: 8001  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Gestión de campañas de marketing
- Creación automática basada en eventos de influencers

**Características**:
- Arquitectura DDD
- Consume eventos de influencers registrados
- Genera eventos de `CampanaCreada`

### 3. Contratos (`contratos/`)

**Puerto**: 8002  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Gestión de contratos entre influencers y campañas
- Procesamiento de términos contractuales

**Características**:
- Arquitectura DDD
- Eventos de integración vía Apache Pulsar
- Genera eventos de `ContratoCreado`

### 4. BFF (`bff/`)

**Puerto**: 8004  
**Base de datos**: No requiere base de datos  
**Funcionalidad**:
- Backend for Frontend que expone endpoints para iniciar el flujo de saga
- Punto de entrada único para el frontend
- Streaming en tiempo real de eventos creados

**Características**:
- Endpoint `/health` para health check
- Endpoint `/influencers` para crear influencer e iniciar el flujo completo
- Endpoint `/stream` para streaming en tiempo real de contratos usando Server-Sent Events (SSE)
- Envía eventos al topic `eventos-influencers` de Pulsar
- Consume eventos del topic `eventos-contratos` de Pulsar
- Arquitectura simple sin persistencia

**Endpoints**:
- `GET /health` - Health check del servicio (200)
- `POST /influencers` - Crea un influencer e inicia el flujo de saga (202 - Accepted)
- `GET /stream` - Streaming en tiempo real de eventos usando SSE (200)

**Request Body para `/influencers`**:
```json
{
  "id_influencer": "string",
  "nombre": "string", 
  "email": "string",
  "categorias": ["string"],
  "plataformas": ["string"], // opcional
  "descripcion": "string", // opcional
  "biografia": "string", // opcional
  "sitio_web": "string", // opcional
  "telefono": "string" // opcional
}
```

**Streaming de Eventos (`/stream`)**:
- **Tecnología**: Server-Sent Events (SSE)
- **Formato**: `text/event-stream`
- **Eventos**:
  - `nuevo_evento`: Nuevos eventos recibidos en tiempo real
  - `error`: Errores del servidor
```

## Infraestructura Compartida

### Apache Pulsar
- **Puerto**: 6650 (cliente), 8080 (API REST)
- **Tópicos**:
  - `eventos-influencers`: Eventos del microservicio de influencers
  - `eventos-campanas`: Eventos del microservicio de campañas
  - `eventos-contratos`: Eventos del microservicio de contratos

### Bases de Datos
- **PostgreSQL**: Puerto 5432 (compartida por todos los microservicios)
  - Base de datos: `alpespartners_dijs`
  - Esquemas separados por microservicio para mantener separación lógica

## Ejecución

### Requisitos
- Docker y Docker Compose
- Python 3.9+ (para desarrollo local)

### Ejecución Completa

```bash
# Desde el directorio raíz
docker-compose up --build -d
```

Esto iniciará todos los servicios:
- Apache Pulsar (6650, 8080)
- PostgreSQL (5432)
- Microservicio Influencers (8000)
- Microservicio Campañas (8001)
- Microservicio Contratos (8002)
- Microservicio BFF (8004)

### Verificación

```bash

# Verificar logs de cada servicio
docker logs alpes-partners-dijs-micros-influencers-1
docker logs alpes-partners-dijs-micros-campanas-1
docker logs alpes-partners-dijs-micros-contratos-1
docker logs alpes-partners-dijs-micros-bff-1
```

### Ejecución Individual

Cada microservicio puede ejecutarse independientemente usando Docker:

```bash
# Microservicio de influencers
cd influencers/
docker build -t influencers .
docker run -p 8000:8080 influencers

# Microservicio de campañas
cd campanas/
docker build -t campanas .
docker run -p 8001:8080 campanas

# Microservicio de contratos
cd contratos/
docker build -t contratos .
docker run -p 8002:8080 contratos

# Microservicio BFF
cd bff/
docker build -t bff .
docker run -p 8004:8080 bff
```

## Flujo de Eventos

1. **Usuario registra influencer** → Consume Evento Influencers 
2. **Influencer se persiste** → PostgreSQL (5432)
3. **Evento `InfluencerRegistrado`** → Pulsar (`eventos-influencers`)
4. **Campañas consume evento** → Microservicio Campañas
5. **Campaña automática se crea** → PostgreSQL (5432)
6. **Evento `CampanaCreada`** → Pulsar (`eventos-campanas`)
7. **Contratos consume evento** → Microservicio Contratos
8. **Contrato se persiste** → PostgreSQL (5432)
9. **Evento `ContratoCreado`** → Pulsar (`eventos-contratos`)

## Implementación del Patrón Saga

### Arquitectura de Orquestación

El sistema implementa el **patrón Saga de Orquestación** para garantizar la consistencia eventual en transacciones distribuidas que abarcan múltiples microservicios. Esta implementación utiliza un coordinador centralizado que gestiona el flujo de la transacción y ejecuta compensaciones cuando es necesario.

### Framework de Sagas (Seedwork)

**Ubicación**: `influencers/src/alpes_partners/seedwork/aplicacion/sagas.py`

El framework base define las interfaces y clases abstractas para implementar sagas:

```python
class CoordinadorSaga(ABC):
    id_correlacion: uuid.UUID
    
    @abstractmethod
    def persistir_en_saga_log(self, mensaje):
        ...
    
    @abstractmethod
    def construir_comando(self, evento: EventoDominio, tipo_comando: type) -> Comando:
        ...
    
    def publicar_comando(self, evento: EventoDominio, tipo_comando: type):
        comando = self.construir_comando(evento, tipo_comando)
        ejecutar_commando(comando)
```

**Clases de Soporte**:

```python
@dataclass
class Transaccion(Paso):
    index: int
    comando: Comando
    evento: EventoDominio
    error: EventoDominio
    compensacion: Comando
    exitosa: bool = False

@dataclass
class Inicio(Paso):
    index: int = 0

@dataclass
class Fin(Paso):
    index: int
```

- `Transaccion`: Define un paso de la saga con comando, evento, error y compensación
- `CoordinadorOrquestacion`: Implementa la lógica de orquestación centralizada
- `CoordinadorCoreografia`: Interfaz para futuras implementaciones de coreografía

### Coordinador de Saga

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/aplicacion/coordinadores/saga_alpes_partners.py`

El coordinador `CoordinadorInfluencersCampanasContratos` implementa la interfaz `CoordinadorOrquestacion` y gestiona el ciclo de vida completo de las transacciones distribuidas:

```python
class CoordinadorInfluencersCampanasContratos(CoordinadorOrquestacion):
    def __init__(self):
        self.id_correlacion = str(uuid.uuid4())
        self.repositorio_saga_log = RepositorioSagaLogSQLAlchemy()
        self.pasos = []
        self.index = 0
        self.contexto_influencer = None
        self.contexto_campana = None
        self.inicializar_pasos()
```

### Definición de Pasos de la Saga

La saga se compone de tres pasos principales con sus respectivas compensaciones:

```python
def inicializar_pasos(self):
    self.pasos = [
        Transaccion(
            index=0,
            comando=CrearInfluencer,
            evento=InfluencerRegistrado,
            error=ErrorCreacionInfluencer,
            compensacion=EliminarInfluencer
        ),
        Transaccion(
            index=1,
            comando=CrearCampana,
            evento=CampanaCreada,
            error=ErrorCreacionCampana,
            compensacion=EliminarCampana
        ),
        Transaccion(
            index=2,
            comando=CrearContrato,
            evento=ContratoCreado,
            error=ErrorCreacionContrato,
            compensacion=EliminarContrato
        )
    ]
```

### Saga Log para Monitoreo

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/infraestructura/repositorio_sqlalchemy.py`

El sistema mantiene un log persistente de todas las transacciones de saga en la tabla `saga_log`:

```sql
CREATE TABLE saga_log (
    id UUID PRIMARY KEY,
    id_correlacion VARCHAR(255) NOT NULL,
    index_paso INTEGER NOT NULL,
    comando VARCHAR(255) NOT NULL,
    evento VARCHAR(255),
    error VARCHAR(255),
    compensacion VARCHAR(255),
    exitosa BOOLEAN DEFAULT FALSE,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos del Saga Log**:
- `id_correlacion`: Identificador único de la transacción distribuida
- `index_paso`: Orden secuencial del paso en la saga
- `comando`: Comando ejecutado en este paso
- `evento`: Evento de éxito generado
- `error`: Evento de error generado
- `compensacion`: Comando de compensación asociado
- `exitosa`: Estado de finalización del paso

### Flujo de Ejecución

#### 1. Inicio de la Saga y Conversión de Eventos
```python
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
            
        elif isinstance(mensaje, ErrorCreacionContrato):
            coordinador.procesar_evento_error_contrato(mensaje)
```

#### 2. Procesamiento de Eventos Exitosos
```python
def procesar_evento_influencer_registrado(self, evento: EventoDominioInfluencerRegistrado):
    self.contexto_influencer = evento
    self._procesar_evento(evento)
    self._ejecutar_siguiente_paso()
```

#### 3. Manejo de Errores y Compensación
```python
def procesar_evento_error_contrato(self, evento: ErrorCreacionContrato):
    logger.error(f"SAGA: Procesando error de contrato - Campaña: {evento.campana_id}")
    
    # Ejecutar compensaciones en orden inverso
    self._ejecutar_compensacion_campana(evento.campana_id)
    self._ejecutar_compensacion_influencer()
```

### Comandos de Compensación

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/aplicacion/comandos/comandos_externos.py`

El sistema define comandos específicos para cada operación de compensación:

```python
@dataclass
class EliminarInfluencer(Comando):
    influencer_id: str
    razon: str = "Compensación por falla en saga"

@dataclass
class EliminarCampana(Comando):
    campana_id: str
    influencer_id: str
    razon: str = "Compensación por falla en saga"

@dataclass
class EliminarContrato(Comando):
    contrato_id: str
    campana_id: str
    influencer_id: str
    razon: str = "Compensación por falla en saga"
```

### Handlers de Compensación

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/aplicacion/handlers.py`

Los handlers ejecutan las operaciones de compensación utilizando los repositorios correspondientes:

```python
@staticmethod
def handle_eliminar_influencer(comando: EliminarInfluencer):
    repositorio = fabrica_repositorio.crear_objeto(RepositorioInfluencersSQLAlchemy)
    repositorio.eliminar(comando.influencer_id)
    logger.info(f"SAGA HANDLER: Influencer {comando.influencer_id} eliminado")
```

### Eventos de Dominio e Integración de la Saga

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/dominio/eventos.py`

El sistema define eventos locales para evitar dependencias directas entre microservicios:

#### **Eventos de Integración (Representaciones Locales)**

```python
class CampanaCreada(EventoIntegracion):
    """Evento local que representa cuando se crea una campaña (desde microservicio campanas)."""
    
    def __init__(self, campana_id: str, nombre: str, descripcion: str, 
                 tipo_comision: str, valor_comision: float, moneda: str,
                 categorias_objetivo: List[str], fecha_inicio: datetime,
                 influencer_id: str = None, influencer_nombre: str = None,
                 influencer_email: str = None):
        super().__init__()
        self.campana_id = campana_id
        self.nombre = nombre
        # ... otros campos

class ContratoCreado(EventoIntegracion):
    """Evento local que representa cuando se crea un contrato (desde microservicio contratos)."""
    
    def __init__(self, contrato_id: str, influencer_id: str, campana_id: str,
                 monto_total: float, moneda: str, fecha_inicio: datetime,
                 fecha_fin: datetime, tipo_contrato: str, fecha_creacion: datetime):
        super().__init__()
        self.contrato_id = contrato_id
        self.influencer_id = influencer_id
        # ... otros campos
```

#### **Eventos de Dominio (Errores y Compensaciones)**

```python
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

class ErrorCreacionInfluencer(EventoDominio):
    """Evento de error cuando falla la creación de influencer."""
    
    def __init__(self, influencer_id: str, error: str):
        super().__init__()
        self.influencer_id = influencer_id
        self.error = error

class CompensacionEjecutada(EventoDominio):
    """Evento que indica que una compensación fue ejecutada exitosamente."""
    
    def __init__(self, comando: str, campana_id: str, influencer_id: str, 
                 razon: str, fecha_ejecucion: datetime):
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
```

#### **Conversión de Eventos de Integración a Dominio**

**Ubicación**: `influencers/src/alpes_partners/modulos/sagas/aplicacion/coordinadores/saga_alpes_partners.py`

El coordinador convierte eventos de integración a eventos de dominio para procesamiento interno:

```python
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
        # ... otros campos

class EventoDominioContratoCreado(EventoDominio):
    """Evento de dominio para contrato creado (conversión desde integración)."""
    
    def __init__(self, evento_integracion: ContratoCreado):
        super().__init__()
        self.contrato_id = evento_integracion.contrato_id
        self.influencer_id = evento_integracion.influencer_id
        self.campana_id = evento_integracion.campana_id
        # ... otros campos
```

### Integración con Pulsar

**Tópicos de Saga**:
- `eventos-contratos-error`: Eventos de error de contratos
- `eventos-campanas-eliminacion-v2`: Comandos de eliminación de campañas
- `eventos-influencers-eliminacion`: Comandos de eliminación de influencers

**Despachadores**:
- `DespachadorSaga`: Publica eventos de compensación
- `ConsumidorSaga`: Procesa eventos de error y ejecuta compensaciones



## Documentación

### Tipos de Eventos de Integración

#### Pregunta de Evaluación
**"Se justifica correctamente los tipos de eventos a utilizar (integración o carga de estado). Ello incluye la definición de los esquemas y evolución de los mismos"**

#### Justificación

En nuestro sistema implementamos **ambos tipos de eventos** porque cada uno cumple un propósito específico:

#### 🔹 **Eventos de Integración**
Los usamos para sincronizar información entre nuestros microservicios. Cuando un influencer se registra, necesitamos que el sistema de campañas se entere para crear campañas automáticamente. Estos eventos se publican en Apache Pulsar y otros servicios los consumen.

#### 🔹 **Eventos con Carga de Estado (Eventos Gordos)**
Los utilizamos cuando necesitamos enviar toda la información de una entidad, no solo lo que cambió. Por ejemplo, cuando creamos una campaña, enviamos todos los datos del influencer asociado para que el sistema de contratos pueda generar el contrato completo sin hacer consultas adicionales.

#### Implementación por Microservicio

#### **1. Microservicio Influencers**

**Evento de Integración**: `InfluencerRegistrado`

**Ubicación**: `influencers/src/alpes_partners/modulos/influencers/infraestructura/schema/eventos.py`

```python
class InfluencerRegistradoPayload(Record):
    """Payload del evento InfluencerRegistrado - Estado Completo"""
    id_influencer = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    fecha_registro = Long()

class EventoInfluencerRegistrado(EventoIntegracion):
    """Evento de integración para influencer registrado"""
    data = InfluencerRegistradoPayload()
```

**¿Por qué lo hacemos así?**: 
- **Integración**: Cuando registramos un influencer, el sistema de campañas necesita enterarse para crear campañas automáticamente
- **Carga de Estado**: Enviamos todos los datos del influencer (nombre, email, categorías) para que campañas no tenga que consultar la base de datos

#### **2. Microservicio Campañas**

**Evento de Integración**: `CampanaCreada`

**Ubicación**: `campanas/src/alpes_partners/modulos/campanas/infraestructura/schema/eventos.py`

```python
class CampanaCreadaPayload(Record):
    """Payload del evento CampanaCreada - Estado Completo"""
    campana_id = String()
    nombre = String()
    descripcion = String()
    tipo_comision = String()
    valor_comision = Float()
    moneda = String(default="USD")
    categorias_objetivo = Array(String())
    fecha_inicio = String()
    fecha_fin = String(default=None, required=False)
    # Campos adicionales para crear contratos
    influencer_id = String(default=None, required=False)
    influencer_nombre = String(default=None, required=False)
    influencer_email = String(default=None, required=False)
    monto_base = Float(default=None, required=False)
    entregables = String(default=None, required=False)
    tipo_contrato = String(default="puntual")
    fecha_creacion = String()

class EventoCampanaCreada(EventoIntegracion):
    """Evento de integración para campaña creada"""
    data = CampanaCreadaPayload()
```

**¿Por qué lo hacemos así?**:
- **Integración**: Cuando creamos una campaña, el sistema de contratos debe generar el contrato automáticamente
- **Carga de Estado**: Enviamos todos los datos de la campaña y del influencer para que contratos no necesite hacer consultas adicionales

#### **3. Microservicio Contratos**

**Evento de Integración**: `ContratoCreado`

**Ubicación**: `contratos/src/alpes_partners/modulos/contratos/infraestructura/schema/v1/eventos.py`

```python
class ContratoCreadoPayload(Record):
    """Payload del evento ContratoCreado - Estado Completo"""
    contrato_id = String()
    influencer_id = String()
    campana_id = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()

class EventoContratoCreado(EventoIntegracion):
    """Evento de integración para contrato creado"""
    data = ContratoCreadaPayload()
```

**¿Por qué lo hacemos así?**:
- **Integración**: Cuando se crea un contrato, reportes debe generar métricas automáticamente
- **Carga de Estado**: Enviamos todos los datos del contrato (montos, fechas, participantes) para que reportes tenga todo lo necesario


### Esquemas y Evolución

#### **Definición de Esquemas Avro**
Todos los eventos usan **Avro Schema** para garantizar compatibilidad:

```python
from pulsar.schema import Record, String, Array, Float, Long
```

#### **Evolución de Esquemas**
- **Campos opcionales**: `required=False` para evolución hacia atrás
- **Valores por defecto**: `default=None` para compatibilidad
- **Versionado**: Esquemas en directorios `v1/` para evolución

**Ejemplo de evolución**:
```python
influencer_email = String(default=None, required=False)  
```

### Conclusión

En resumen, usamos **ambos tipos de eventos** porque:

1. **Eventos de Integración**: Nos permiten que los microservicios se comuniquen entre sí de forma asíncrona
2. **Eventos con Carga de Estado**: Evitamos que los servicios tengan que hacer consultas adicionales a la base de datos

Esta combinación nos da un sistema donde cada microservicio puede trabajar de forma independiente, pero siempre con la información que necesita para funcionar correctamente.

## Topologías para la Administración de Datos

### Pregunta de Evaluación
**"Definió, justificó e implementó alguna de las topologías para la administración de datos?"**

### Topología Implementada: **Híbrida**

En nuestro proyecto decidimos usar una **topología híbrida** porque nos permite balancear costos, complejidad y flexibilidad.

#### ¿Por qué elegimos la topología híbrida?

**Ventajas que nos interesan:**
- **Reducción de costos**: No necesitamos 4 bases de datos separadas, lo que reduce costos de infraestructura
- **Administración simplificada**: Un solo equipo puede manejar la base de datos
- **Independencia lógica**: Cada microservicio tiene su propio esquema, manteniendo separación de datos

**Desventajas que manejamos:**
- **Acoplamiento controlado**: Aunque compartimos la base física, cada servicio tiene su esquema independiente
- **Riesgo de monolito**: Lo evitamos usando esquemas separados y no compartiendo tablas

### Implementación en Nuestros Microservicios

#### **Estructura de Base de Datos**

```sql
-- Base de datos compartida: alpespartners_dijs
-- Puerto: 5432

-- Esquemas separados por microservicio:
- influencers_schema    -- Microservicio Influencers
- campanas_schema       -- Microservicio Campañas  
- contratos_schema      -- Microservicio Contratos
```

#### **Ejemplos de Implementación**

**1. Microservicio Influencers**
```python
# influencers/src/alpes_partners/seedwork/infraestructura/database.py
class InfluencerDB(DeclarativeBase):
    __tablename__ = 'influencers'
    __table_args__ = {'schema': 'influencers_schema'}
    
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    categorias = Column(JSON)
```

**2. Microservicio Campañas**
```python
# campanas/src/alpes_partners/seedwork/infraestructura/database.py
class CampanaDB(DeclarativeBase):
    __tablename__ = 'campanas'
    __table_args__ = {'schema': 'campanas_schema'}
    
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    influencer_origen_id = Column(String)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
```

**3. Microservicio Contratos**
```python
# contratos/src/alpes_partners/seedwork/infraestructura/database.py
class ContratoDB(DeclarativeBase):
    __tablename__ = 'contratos'
    __table_args__ = {'schema': 'contratos_schema'}
    
    id = Column(String, primary_key=True)
    influencer_id = Column(String, nullable=False)
    campana_id = Column(String, nullable=False)
    monto_total = Column(Float)
    fecha_creacion = Column(DateTime)
```

### ¿Por qué no las otras topologías?

#### **Topología Centralizada**
- **Problema**: Un solo esquema compartido crearía alto acoplamiento
- **Ejemplo de lo que evitaríamos**: 
  ```sql
  -- MAL: Tabla compartida
  CREATE TABLE datos_compartidos (
      influencer_id VARCHAR,
      campana_id VARCHAR,
      contrato_id VARCHAR
  );
  ```

#### **Topología Descentralizada**
- **Problema**: 4 bases de datos separadas serían costosas y complejas
- **Ejemplo de lo que evitaríamos**:
  ```yaml
  # docker-compose.yml - MAL: Múltiples bases de datos
  services:
    postgres-influencers:
      image: postgres:13
    postgres-campanas:
      image: postgres:13
    postgres-contratos:
      image: postgres:13
  ```

### Configuración de Conexión

**Docker Compose - Una sola base de datos:**
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: alpespartners_dijs
    ports:
      - "5432:5432"
  
  influencers:
    environment:
      DATABASE_URL: "postgresql://postgres:password@postgres:5432/alpespartners_dijs"
  
  campanas:
    environment:
      DATABASE_URL: "postgresql://postgres:password@postgres:5432/alpespartners_dijs"
```

### Ventajas de Nuestra Implementación

1. **Costo-efectiva**: Una sola instancia de PostgreSQL
2. **Mantenimiento simple**: Un solo punto de administración
3. **Independencia lógica**: Esquemas separados evitan acoplamiento
4. **Escalabilidad**: Cada esquema puede crecer independientemente
5. **Consistencia**: Transacciones ACID dentro de cada esquema

### Conclusión

La topología híbrida nos permite tener lo mejor de ambos mundos: la simplicidad operativa de una base centralizada con la independencia lógica de bases descentralizadas. Cada microservicio mantiene su autonomía de datos a través de esquemas separados, pero compartimos la infraestructura para reducir costos y complejidad.

### Modelo CRUD + Pulsar

#### Justificación del Modelo Elegido

En nuestro proyecto implementamos el **modelo CRUD + Pub/Sub** (en nuestro caso, CRUD + Pulsar), que representa una mejora significativa sobre la topología CRUD tradicional.

Este modelo es una **mejora a la topología CRUD** donde publicamos eventos de los cambios sucedidos de forma asíncrona. Los servicios externos pueden beneficiarse de esta topología gracias al consumo de eventos.

El modelo CRUD + Pulsar nos permite mantener la simplicidad de las operaciones CRUD mientras obtenemos los beneficios de la comunicación orientada a eventos, siendo una solución equilibrada para nuestro contexto de microservicios.

### Descripción de Actividades por Miembro del Equipo

**Sergio Celis**
- Desarrollo del BFF

**Diego Jaramillo**
- Desarrollo del BFF

**Julio Sánchez**
- Desarrollo e implementación de la SAGA
- Configuración y despliegue de la solución en Google Cloud Platform (GCP)

**Ian Beltrán**
- Desarrollo e implementación de la SAGA
- Configuración y despliegue de la solución en Google Cloud Platform (GCP)

## Desarrollo

### Estructura DDD

Todos los microservicios siguen la misma estructura DDD:

```
src/a
└── alpes_partners/
    ├── api/                    # Capa de presentación (solo para pruebas)
    ├── config/                 # Configuración
    ├── modulos/
    │   └── {modulo}/
    │       ├── aplicacion/     # Casos de uso, comandos, DTOs
    │       ├── dominio/        # Entidades, eventos, repositorios
    │       └── infraestructura/ # Persistencia, eventos, schemas
    └── seedwork/               # Componentes reutilizables
        ├── aplicacion/
        ├── dominio/
        ├── infraestructura/
        └── presentacion/
```

## Despliegue en GCP

### Despliegue Pulsar en VM

1. Ejecutar el `scripts-despliegue-pulsar-vm-gcp/create-vm.sh` para crear la VM en GCP
Nota: Si generar error de permisos correr `chmod +x create-vm.sh`

2. Ejecutar el `scripts-despliegue-pulsar-vm-gcp/startup-script.sh` para instalar pulsar y levantarlo con docker
Nota: Si generar error de permisos correr `chmod +x startup-script.sh`

3. Antes de desplegar los microservicios, cambiar la variable de entorno `PULSAR_ADDRESS` por la IP externa de la VM

### Configuración de VPC Connector

Para conectar de forma segura los microservicios de Cloud Run con Pulsar en la VM, se recomienda usar un Serverless VPC Connector. Esto permite que los servicios se comuniquen usando la red interna de GCP.

#### Configurar VPC Connector

**1. Creacion SubNet**
```bash
gcloud compute networks subnets create pulsar-connector-subnet \
    --network=default \
    --range=10.8.0.0/28 \
    --region=us-central1 \
    --description="Subnet para VPC Connector de Pulsar"
```

**2. Crear Serverless VPC Connector**
```bash
gcloud compute networks vpc-access connectors create pulsar-vpc-connector \
    --region=us-central1 \
    --subnet=pulsar-connector-subnet \
    --subnet-project=uniandes-native-202511 \
    --min-instances=2 \
    --max-instances=10 \
    --machine-type=e2-micro
```

**3. Crear regla de firewall para permitir tráfico desde VPC Connector**
```bash
gcloud compute firewall-rules create allow-vpc-connector-to-pulsar \
    --allow tcp:6650,tcp:8080,tcp:5432 \
    --source-ranges 10.8.0.0/28 \
    --target-tags pulsar-server \
    --description "Allow VPC Connector traffic to Pulsar VM"
```

### Despliegue Microservicios en Cloud Run (Método Tradicional)

1. Crear la Base de datos en al **Cloud SQL** en la cuenta de **GCP**.

2. Genera la imagen Docker del microservicio utilizando el siguiente comando:
```bash
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/saga:1.0 .
docker build -f Dockerfile.saga -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/saga:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/bff:1.0 .
```

Para arquitectura amd64
```bash
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build -f Dockerfile.saga --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/saga:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/bff:1.0 .
```

3. Subir la imagen al **Artifactory Registry** creado en la cuenta de **GCP** con el siguiente comando:
```bash
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/saga:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/bff:1.0
```

4. Desplegar los servicio en Cloud Run

Microservicio Influencers
```bash
gcloud run deploy influencers-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:Postgres-1@IP_DB:5432/postgres",PULSAR_ADDRESS=IP_PULSAR_INTERNA,RECREATE_DB=false\
    --vpc-connector pulsar-vpc-connector \
    --memory 32Gi \
    --cpu 8 \
    --min-instances 1 \
    --max-instances 10 \
    --execution-environment gen2
```

Microservicio Campañas
```bash
gcloud run deploy campanas-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:Postgres-1@IP_DB:5432/postgres",PULSAR_ADDRESS=IP_PULSAR_INTERNA,RECREATE_DB=false\
    --vpc-connector pulsar-vpc-connector \
    --memory 32Gi \
    --cpu 8 \
    --min-instances 1 \
    --max-instances 10 \
    --execution-environment gen2
```

Microservicio Contratos
```bash
gcloud run deploy contratos-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:Postgres-1@IP_DB:5432/postgres",PULSAR_ADDRESS=IP_PULSAR_INTERNA,RECREATE_DB=false\
    --vpc-connector pulsar-vpc-connector \
    --memory 32Gi \
    --cpu 8 \
    --min-instances 1 \
    --max-instances 10 \
    --execution-environment gen2
```

Saga
```bash
gcloud run deploy saga-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/saga:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:Postgres-1@IP_DB:5432/postgres",PULSAR_ADDRESS=IP_PULSAR_INTERNA,RECREATE_DB=false\
    --vpc-connector pulsar-vpc-connector \
    --memory 32Gi \
    --cpu 8 \
    --min-instances 1 \
    --max-instances 10 \
    --execution-environment gen2
```

BFF
```bash
gcloud run deploy bff-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/bff:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:Postgres-1@IP_DB:5432/postgres",PULSAR_ADDRESS=IP_PULSAR_INTERNA,RECREATE_DB=false\
    --vpc-connector pulsar-vpc-connector \
    --memory 32Gi \
    --cpu 8 \
    --min-instances 1 \
    --max-instances 10 \
    --execution-environment gen2
```

## Scripts envio eventos pulsar

```bash
# Instalar cliente de Pulsar con soporte Avro
pip3 install 'pulsar-client[avro]'
```

### Configuración

El script usa las siguientes configuraciones:

- **Broker Pulsar**: `localhost:6650` (por defecto)
- **Tópico**: `eventos-contratos`
- **Esquema**: Avro con payload de contrato

### Variables de Entorno

```bash
# Si Pulsar está en otro servidor
export PULSAR_ADDRESS=tu-servidor-pulsar

# Ejemplo para GCP
export PULSAR_ADDRESS=34.123.45.67
```

### Ejecución

```bash
# Ejecución básica (usa localhost)
python scripts-envio-eventos-pulsar/enviar_evento_crear_influencer_pulsar.py

# Con servidor remoto
PULSAR_ADDRESS=mi-servidor-pulsar python scripts-envio-eventos-pulsar/enviar_evento_crear_influencer_pulsar.py

# Hacer ejecutable (opcional)
chmod +x scripts-envio-eventos-pulsar/enviar_evento_crear_influencer_pulsar.py
./scripts-envio-eventos-pulsar/enviar_evento_crear_influencer_pulsar.py
```

### Datos del Evento

El script envía un evento con la siguiente estructura:

```json
{
  "data": {
    "id_contrato": "fdad3d32-f6ea-4836-bc11-bb622036ab7c",
    "id_influencer": "inf-12345",
    "id_campana": "camp-67890",
    "monto_total": 2500.0,
    "moneda": "USD",
    "tipo_contrato": "temporal",
    "fecha_creacion": "2025-09-13 01:07:56.578686"
  }
}
```