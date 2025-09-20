# BFF API - Documentación Completa

## Descripción General

El microservicio BFF (Backend for Frontend) actúa como punto de entrada único, proporcionando endpoints para interactuar con el sistema de Alpes Partners. Este servicio se encarga de recibir las solicitudes del frontend o cliente para iniciar los flujos de procesamiento asíncrono.

## Información del Servicio

- **Nombre**: BFF Microservice
- **Versión**: 1.0.0
- **Puerto**: 8004
- **Base URL**: `http://localhost:8004`
- **Arquitectura**: Backend for Frontend con comunicación asíncrona vía Apache Pulsar

## Inicio Rápido

### 1. Importar Collection de Postman

1. Abre Postman
2. Haz clic en "Import"
3. Selecciona el archivo `BFF Alpes Partners API.postman_collection.json`
4. La collection se importará con todas las requests configuradas

### 2. Configurar Variables

La collection incluye una variable `base_url` configurada por defecto como:
```
http://localhost:8004
```

Si tu BFF está ejecutándose en un puerto diferente, actualiza la variable en Postman.

### 3. Ejecutar Requests

#### Health Check
- **Request**: `GET /health`
- **Propósito**: Verificar que el servicio esté funcionando
- **Response esperado**: `200 OK`

#### Crear Influencer
- **Request**: `POST /influencers`
- **Propósito**: Crear un nuevo influencer e iniciar el flujo de saga
- **Response esperado**: `202 Accepted`

#### Stream de Eventos
- **Request**: `GET /stream`
- **Propósito**: Obtener streaming en tiempo real de eventos creados
- **Response esperado**: `200 OK` (text/event-stream)

## Endpoints Disponibles

### 1. Health Check

Verifica el estado del servicio.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "up",
  "service": "bff-microservice",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Servicio funcionando correctamente
- `500 Internal Server Error`: Error interno del servidor

---

### 2. Crear Influencer

Crea un nuevo influencer e inicia el flujo de saga de forma asíncrona.

**Endpoint**: `POST /influencers`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "id_influencer": "string",
  "nombre": "string",
  "email": "string",
  "categorias": ["string"],
  "plataformas": ["string"],
  "descripcion": "string",
  "biografia": "string",
  "sitio_web": "string",
  "telefono": "string"
}
```

**Campos Requeridos**:
- `id_influencer`: ID único del influencer
- `nombre`: Nombre del influencer
- `email`: Email del influencer
- `categorias`: Lista de categorías del influencer

**Campos Opcionales**:
- `plataformas`: Lista de plataformas del influencer (default: `[]`)
- `descripcion`: Descripción del influencer (default: `""`)
- `biografia`: Biografía del influencer (default: `""`)
- `sitio_web`: Sitio web del influencer (default: `""`)
- `telefono`: Teléfono del influencer (default: `""`)

**Response**:
```json
{
  "success": true,
  "message": "Influencer procesado"
}
```

**Status Codes**:
- `202 Accepted`: Influencer procesado (operación asíncrona)
- `400 Bad Request`: Error en la validación de datos
- `500 Internal Server Error`: Error interno del servidor

**Ejemplo de Request**:
```json
{
  "id_influencer": "inf-001",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "categorias": ["tecnologia", "gaming"],
  "plataformas": ["instagram", "youtube", "tiktok"],
  "descripcion": "Influencer de tecnología y gaming",
  "biografia": "Apasionado por la tecnología y los videojuegos",
  "sitio_web": "https://juanperez.com",
  "telefono": "+1234567890"
}
```

**Ejemplo de Response**:
```json
{
  "success": true,
  "message": "Influencer procesado"
}
```

---

### 3. Stream de Eventos

Obtiene un stream en tiempo real de eventos usando Server-Sent Events (SSE).

**Endpoint**: `GET /stream`

**Content-Type**: `text/event-stream`

**Descripción**: Este endpoint mantiene una conexión abierta y envía actualizaciones en tiempo real cada vez que se crea un nuevo evento en el sistema. El stream se suscribe automáticamente al tópico `eventos-contratos` de Apache Pulsar.

**Response Format**:
```
Nuevo evento
{
    "data": {
        "fecha_creacion": "2025-09-20 03:21:45.872565",
        "id_campana": "9bc31edd-0540-4e63-a696-67bdc38642c5",
        "id_contrato": "5ebfe61c-3f85-4192-a1df-9724e8c1797f",
        "id_influencer": "a6cb7081-7127-474d-b7ab-4988cd1a35f3"
    }
}
```

**Estructura de Datos**:
- Cada línea contiene "Nuevo evento" seguido del JSON
- El JSON contiene un objeto `data` con un array `eventos`
- Cada evento incluye:
  - `fecha_creacion`: Timestamp de creación del evento
  - `id_campana`: ID de la campaña asociada
  - `id_contrato`: ID único del contrato
  - `id_influencer`: ID del influencer asociado

**Headers de Response**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Cache-Control
```

**Status Codes**:
- `200 OK`: Stream iniciado correctamente
- `500 Internal Server Error`: Error interno del servidor

```

## Códigos de Error

### 400 Bad Request
```json
{
  "error": "Campo requerido: nombre"
}
```

### 400 Bad Request (Content-Type inválido)
```json
{
  "error": "Content-Type debe ser application/json"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error interno del servidor: [detalle del error]"
}
```

## Collection de Postman Incluida

La collection incluye los siguientes requests:

1. **Health Check** - Verificar estado del servicio
2. **Crear Influencer - Exitoso** - Con todos los campos disponibles
3. **Crear Influencer - Error Validación** - Ejemplo de error de validación

## Códigos de Respuesta

| Código | Descripción | Cuándo ocurre |
|--------|-------------|---------------|
| `200` | OK | Health check exitoso, información del servicio, stream iniciado |
| `202` | Accepted | Influencer procesado (asíncrono) |
| `400` | Bad Request | Error de validación o Content-Type incorrecto |
| `500` | Internal Server Error | Error interno del servidor |

## Configuración del Entorno

### Variables de Entorno
- `PULSAR_ADDRESS`: Dirección del broker de Pulsar (default: `pulsar`)
- `ENVIRONMENT`: Entorno de ejecución (default: `development`)
- `LOG_LEVEL`: Nivel de logging (default: `INFO`)

### Dependencias
- Apache Pulsar debe estar ejecutándose
- El topic `eventos-crear-influencer` debe estar disponible (para crear influencers)
- El topic `eventos-contratos` debe estar disponible (para el stream de contratos)
- Los microservicios de destino deben estar funcionando

### Levantar el Sistema

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar que el BFF esté funcionando
curl http://localhost:8004/health

# Ver logs del BFF
docker logs alpes-partners-dijs-micros-bff-1
```

## Ejemplos de Uso

### cURL
```bash
# Health check
curl -X GET http://localhost:8004/health

# Crear influencer (completo)
curl -X POST http://localhost:8004/influencers \
  -H "Content-Type: application/json" \
  -d '{
    "id_influencer": "inf-002",
    "nombre": "María García",
    "email": "maria.garcia@example.com",
    "categorias": ["lifestyle", "moda"],
    "plataformas": ["instagram", "youtube"],
    "descripcion": "Influencer de lifestyle",
    "biografia": "Apasionada por la moda",
    "sitio_web": "https://mariagarcia.com",
    "telefono": "+1234567890"
  }'

# Stream de eventos (tiempo real)
curl -N http://localhost:8004/stream
```

## Archivos de la Documentación

- **`BFF_API_DOCUMENTATION.md`**: Esta documentación completa
- **`BFF_Postman_Collection.json`**: Collection de Postman lista para importar
