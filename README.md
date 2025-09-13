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
- Arquitectura DDD con capas bien definidas
- Consume eventos de influencers registrados
- Genera eventos de `CampanaCreada`

### 3. Contratos (`contratos/`)

**Puerto**: 8002  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Gestión de contratos entre influencers y campañas
- Procesamiento de términos contractuales

**Características**:
- Arquitectura DDD con capas bien definidas
- Eventos de integración vía Apache Pulsar
- Genera eventos de `ContratoCreado`

### 4. Reportes (`reportes/`)

**Puerto**: 8003  
**Base de datos**: PostgreSQL (puerto 5432)  
**Funcionalidad**:
- Generación automática de reportes basados en eventos
- Consumo de eventos de contratos creados

**Características**:
- Consume eventos de `ContratoCreado`
- Genera reportes automáticamente

## Infraestructura Compartida

### Apache Pulsar
- **Puerto**: 6650 (cliente), 8080 (API REST)
- **Tópicos**:
  - `eventos-influencers`: Eventos del microservicio de influencers
  - `eventos-campanas`: Eventos del microservicio de campañas
  - `eventos-contratos`: Eventos del microservicio de contratos
  - `eventos-reportes`: Eventos del microservicio de reportes
  - `video-detectado`: Eventos de detección de videos

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

1. Ejecutar el `scripts-despliegue-pulsar-vm-gcp/create-vm.sh` para crear la VM en GCP
Nota: Si generar error de permisos correr `chmod +x create-vm.sh`

2. Ejecutar el `scripts-despliegue-pulsar-vm-gcp/startup-script.sh` para instalar pulsar y levantarlo con docker
Nota: Si generar error de permisos correr `chmod +x startup-script.sh`

3. Antes de desplegar los microservicios, cambiar la variable de entorno `PULSAR_ADDRESS` por la IP externa de la VM

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