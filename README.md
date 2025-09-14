# Arquitectura de Microservicios - Alpes Partners

Este repositorio contiene la implementación de microservicios para Alpes Partners, siguiendo principios de Domain Driven Design (DDD) y arquitectura orientada a eventos.

## Estructura del Proyecto

```
alpes-partners-dijs-micros/
├── influencers/                  # Microservicio de Influencers
├── campanas/                     # Microservicio de Campañas
├── contratos/                    # Microservicio de Contratos
├── reportes/                     # Microservicio de Reportes
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

### 4. Reportes (`reportes/`)

**Puerto**: 8003  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Generación automática de reportes basados en eventos
- Consumo de eventos de contratos creados

**Características**:
- Arquitectura DDD
- Consume eventos de Contratos creados
- Genera eventos de `ReporteCreado`

## Infraestructura Compartida

### Apache Pulsar
- **Puerto**: 6650 (cliente), 8080 (API REST)
- **Tópicos**:
  - `eventos-influencers`: Eventos del microservicio de influencers
  - `eventos-campanas`: Eventos del microservicio de campañas
  - `eventos-contratos`: Eventos del microservicio de contratos
  - `eventos-reportes`: Eventos del microservicio de reportes

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
- Microservicio Reportes (8003)

### Verificación

```bash

# Verificar logs de cada servicio
docker logs alpes-partners-dijs-micros-influencers-1
docker logs alpes-partners-dijs-micros-campanas-1
docker logs alpes-partners-dijs-micros-contratos-1
docker logs alpes-partners-dijs-micros-reportes-1
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

# Microservicio de reportes
cd reportes/
docker build -t reportes .
docker run -p 8003:8080 reportes
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
10. **Reportes consume evento** → Microservicio Reportes
11. **Reporte se crea automáticamente** → PostgreSQL (5432)
12. **Evento `ReporteCreado`** → Pulsar (`eventos-reportes`)

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

#### **4. Microservicio Reportes**

**Evento de Integración**: `ReporteCreado`

**Ubicación**: `reportes/src/alpes_partners/modulos/reportes/infraestructura/schema/eventos.py`

```python
class ReporteCreadoPayload(Record):
    """Payload del evento ReporteCreado - Estado Completo"""
    reporte_id = String()
    tipo_reporte = String()
    fecha_generacion = String()
    datos_reporte = String()  
    contratos_incluidos = Array(String())

class EventoReporteCreado(EventoIntegracion):
    """Evento de integración para reporte creado"""
    data = ReporteCreadoPayload()
```

**¿Por qué lo hacemos así?**:
- **Integración**: Cuando generamos un reporte, otros sistemas pueden consumirlo para análisis
- **Carga de Estado**: Enviamos todas las métricas y datos agregados para que otros sistemas tengan la información completa

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
- reportes_schema       -- Microservicio Reportes
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

**4. Microservicio Reportes**
```python
# reportes/src/alpes_partners/seedwork/infraestructura/database.py
class ReporteDB(DeclarativeBase):
    __tablename__ = 'reportes'
    __table_args__ = {'schema': 'reportes_schema'}
    
    id = Column(String, primary_key=True)
    tipo_reporte = Column(String)
    datos_reporte = Column(JSON)
    fecha_generacion = Column(DateTime)
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
      contrato_id VARCHAR,
      reporte_id VARCHAR
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
    postgres-reportes:
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
- Desarrollo completo del microservicio de Campañas
- Definición y especificación de los 3 escenarios de calidad

**Diego Jaramillo**
- Desarrollo completo del microservicio de Influencers
- Definición y especificación de los 3 escenarios de calidad

**Julio Sánchez**
- Desarrollo del microservicio de Contratos
- Implementación y ajustes de comunicación orientada a eventos
- Configuración y despliegue de la solución en Google Cloud Platform (GCP)

**Ian Beltrán**
- Desarrollo del microservicio de Reportes
- Implementación y ajustes de comunicación orientada a eventos
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

### Despliegue Microservicios en Cloud Run

1. Crear la Base de datos en al **Cloud SQL** en la cuenta de **GCP**.

2. Genera la imagen Docker del microservicio utilizando el siguiente comando:
```bash
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0 .
```

Para arquitectura amd64
```bash
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0 .
```

3. Subir la imagen al **Artifactory Registry** creado en la cuenta de **GCP** con el siguiente comando:
```bash
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0
```

4. Desplegar los servicio en Cloud Run

Microservicio Influencers
```bash
gcloud run deploy influencers-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/influencers:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:passwordDB10@IP_DB:5432/postgres",PULSAR_ADDRESS="IP_VM",RECREATE_DB=false\
    --memory 16Gi \
    --cpu 4 \
    --min-instances 1 \
    --max-instances 1
```

Microservicio Campañas
```bash
gcloud run deploy campanas-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/campanas:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:passwordDB10@IP_DB:5432/postgres",PULSAR_ADDRESS="IP_VM",RECREATE_DB=false\
    --memory 16Gi \
    --cpu 4 \
    --min-instances 1 \
    --max-instances 1
```

Microservicio Contratos
```bash
gcloud run deploy contratos-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:passwordDB10@IP_DB:5432/postgres",PULSAR_ADDRESS="IP_VM",RECREATE_DB=false\
    --memory 16Gi \
    --cpu 4 \
    --min-instances 1 \
    --max-instances 1
```

Microservicio Reportes
```bash
gcloud run deploy reportes-ms \
    --image us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0 \
    --region us-central1 \
    --set-env-vars DATABASE_URL="postgresql://postgres:passwordDB10@IP_DB:5432/postgres",PULSAR_ADDRESS="IP_VM",RECREATE_DB=false\
    --memory 16Gi \
    --cpu 4 \
    --min-instances 1 \
    --max-instances 1
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
python scripts-envio-eventos-pulsar/enviar_evento_reportes_pulsar.py

# Con servidor remoto
PULSAR_ADDRESS=mi-servidor-pulsar python scripts-envio-eventos-pulsar/enviar_evento_reportes_pulsar.py

# Hacer ejecutable (opcional)
chmod +x scripts-envio-eventos-pulsar/enviar_evento_reportes_pulsar.py
./scripts-envio-eventos-pulsar/enviar_evento_reportes_pulsar.py
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