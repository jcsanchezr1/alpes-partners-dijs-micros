# Arquitectura de Microservicios - Alpes Partners

Este repositorio contiene la implementación de microservicios para Alpes Partners, siguiendo principios de Domain Driven Design (DDD) y arquitectura orientada a eventos.

## Estructura del Proyecto

```
alpes-partners-dijs-micros/
├── alpes-partners-dijs/          # Microservicio principal (Influencers y Campañas)
├── reportes/                     # Microservicio de Reportes
├── docker-compose.yml            # Orquestación completa de microservicios
└── README.md                     # Este archivo
```

## Microservicios

### 1. Alpes Partners DIJS (`alpes-partners-dijs/`)

**Puerto**: 8000  
**Base de datos**: PostgreSQL (puerto 5432)  
**Módulos**:
- **Influencers**: Gestión de influencers y registro
- **Campañas**: Gestión de campañas de marketing

**Características**:
- Arquitectura DDD con capas bien definidas
- Eventos de integración via Apache Pulsar
- API REST para operaciones CRUD
- Consumidor de eventos entre módulos

### 2. Reportes (`reportes/`)

**Puerto**: Ninguno (completamente asíncrono)  
**Base de datos**: PostgreSQL (puerto 5433)  
**Funcionalidad**:
- Generación automática de reportes basados en eventos
- Consumo de eventos de campañas creadas
- Soporte para patrón Saga (compensación)

**Características**:
- **Completamente asíncrono** (igual que el módulo campañas)
- Consume eventos de `CampanaCreada` del microservicio principal
- Genera reportes automáticamente
- Estado de reportes con soporte para cancelación
- TODO: Consumir eventos de contrato cuando estén disponibles

## Infraestructura Compartida

### Apache Pulsar
- **Puerto**: 6650 (cliente), 8080 (API REST)
- **Tópicos**:
  - `eventos-influencers`: Eventos del módulo de influencers
  - `eventos-campanas`: Eventos del módulo de campañas
  - `eventos-reportes`: Eventos del microservicio de reportes
  - `eventos-contratos`: (TODO) Eventos de contrato

### Bases de Datos
- **PostgreSQL Alpes**: Puerto 5432 (influencers y campañas)
- **PostgreSQL Reportes**: Puerto 5433 (reportes)

## Ejecución

### Requisitos
- Docker y Docker Compose
- Python 3.9+ (para desarrollo local)

### Ejecución Completa

```bash
# Desde el directorio raíz
docker-compose up --build
```

Esto iniciará todos los servicios:
- Apache Pulsar (6650, 8080)
- PostgreSQL para Alpes Partners (5432)
- PostgreSQL para Reportes (5433)
- Microservicio Alpes Partners (8000)
- Consumidor de eventos Alpes Partners
- Microservicio de Reportes (solo consumidor)
- Consumidor de eventos de Reportes

### Verificación

```bash
# Health check del servicio principal
curl http://localhost:8000/

# Verificar logs del servicio de reportes (no tiene API)
docker logs reportes-app

# API de influencers
curl http://localhost:8000/influencers

# API de campañas
curl http://localhost:8000/campanas

# Verificar logs de reportes 
docker logs reportes-app
```

### Ejecución Individual

Cada microservicio puede ejecutarse independientemente:

```bash
# Solo el microservicio de reportes
cd reportes/
docker-compose up --build -d

# Solo el microservicio principal
cd alpes-partners-dijs/
docker-compose up --build -d
```

## Flujo de Eventos

### Escenario: Creación de Campaña

1. **Usuario crea campaña** → API Alpes Partners (8000)
2. **Campaña se persiste** → PostgreSQL Alpes (5432)
3. **Evento `CampanaCreada`** → Pulsar (`eventos-campanas`)
4. **Reportes consume evento** → Consumidor de Reportes
5. **Reporte se crea automáticamente** → PostgreSQL Reportes (5433)
6. **Evento `ReporteCreado`** → Pulsar (`eventos-reportes`)

### Escenario: Registro de Influencer

1. **Usuario registra influencer** → API Alpes Partners (8000)
2. **Influencer se persiste** → PostgreSQL Alpes (5432)
3. **Evento `InfluencerRegistrado`** → Pulsar (`eventos-influencers`)
4. **Campañas consume evento** → Consumidor interno
5. **Campaña automática se crea** → PostgreSQL Alpes (5432)
6. **Evento `CampanaCreada`** → Pulsar (`eventos-campanas`)
7. **Reportes consume evento** → Microservicio de Reportes
8. **Reporte se genera** → PostgreSQL Reportes (5433)

## Desarrollo

### Estructura DDD

Ambos microservicios siguen la misma estructura DDD:

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

1. Ejecutar el `pulsar-vm/create-vm.sh` para crear la VM en GCP
Nota: Si generar error de permisos correr `chmod +x create-vm.sh`

2. Ejecutar el `pulsar-vm/startup-script.sh` para instalar pulsar y levantarlo con docker
Nota: Si generar error de permisos correr `chmod +x startup-script.sh`

3. Antes de desplegar los microservicios, cambiar la variable de entorno `PULSAR_ADDRESS` por la IP externa de la VM

## Script de Envío de Eventos a Pulsar

Se incluye un script independiente para enviar eventos de contrato creado directamente a Pulsar.

### Archivo: `enviar_evento_pulsar.py`

### Despliegue Microservicios en Cloud Run

1. Crear la Base de datos en al **Cloud SQL** en la cuenta de **GCP**.

2. Genera la imagen Docker del microservicio utilizando el siguiente comando:
```bash
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0 .
```

Para arquitectura amd64
```bash
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0 .
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0 .
```

3. Subir la imagen al **Artifactory Registry** creado en la cuenta de **GCP** con el siguiente comando:
```bash
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/contratos:1.0
docker push us-central1-docker.pkg.dev/uniandes-native-202511/dijis-alpes-partners/reportes:1.0
```

4. Desplegar los servicio en Cloud Run
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

### Requisitos

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
python enviar_evento_pulsar.py

# Con servidor remoto
PULSAR_ADDRESS=mi-servidor-pulsar python enviar_evento_pulsar.py

# Hacer ejecutable (opcional)
chmod +x enviar_evento_pulsar.py
./enviar_evento_pulsar.py
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