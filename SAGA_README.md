# Coordinador de Saga - Influencers → Campañas → Contratos

## Problema Resuelto

La saga estaba implementada en `influencers/src/alpes_partners/modulos/sagas/aplicacion/coordinadores/saga_reservas.py` pero **no estaba escuchando eventos de Pulsar**. Solo usaba `pydispatch` para eventos internos, pero los eventos de los microservicios se publican en Pulsar.

## Solución Implementada

### 1. Consumidor de Pulsar para la Saga

**Archivo**: `influencers/src/alpes_partners/modulos/sagas/infraestructura/consumidores.py`

- Escucha 3 tópicos de Pulsar en paralelo:
  - `eventos-influencers` → `InfluencerRegistrado`
  - `eventos-campanas` → `CampanaCreada`
  - `eventos-contratos` → `ContratoCreado`

- Convierte eventos de Pulsar a eventos de dominio
- Invoca la función `oir_mensaje` de la saga

### 2. Script de Ejecución

**Archivo**: `influencers/run_saga.py`

- Ejecuta la saga como un servicio independiente
- Health check en puerto 8084
- Consumidores de Pulsar en hilos daemon

### 3. Configuración Docker

**Archivo**: `docker-compose.yml`

- Nuevo servicio `saga` en puerto 8084
- Depende de todos los otros microservicios
- Usa la misma imagen de `influencers`

## Cómo Usar

### Ejecutar con Docker Compose

```bash
# Levantar todos los servicios incluyendo la saga
docker-compose up -d

# Verificar que la saga esté funcionando
curl http://localhost:8084/health
```

### Ejecutar Solo la Saga (para desarrollo)

```bash
cd influencers/
python run_saga.py
```

### Logs de la Saga

```bash
# Ver logs del contenedor de saga
docker-compose logs -f saga

# Buscar logs específicos de la saga
docker-compose logs saga | grep "SAGA:"
```

## Flujo de la Saga

1. **Usuario registra influencer** → Microservicio Influencers
2. **Evento `InfluencerRegistrado`** → Pulsar (`eventos-influencers`)
3. **🔥 SAGA escucha y procesa** → Crea comando `RegistrarCampana`
4. **Campaña se crea** → Microservicio Campañas
5. **Evento `CampanaCreada`** → Pulsar (`eventos-campanas`)
6. **🔥 SAGA escucha y procesa** → Crea comando `CrearContrato`
7. **Contrato se crea** → Microservicio Contratos
8. **Evento `ContratoCreado`** → Pulsar (`eventos-contratos`)
9. **🔥 SAGA escucha y finaliza** → Marca saga como completada

## Verificar que Funciona

### 1. Verificar Health Check

```bash
curl http://localhost:8084/
# Respuesta: {"status":"healthy","service":"saga-coordinator"}
```

### 2. Crear un Influencer y Observar Logs

```bash
# Crear influencer (esto debería disparar toda la saga)
curl -X POST http://localhost:8000/influencers \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Saga",
    "email": "saga@test.com",
    "categorias": ["tech", "gaming"]
  }'

# Observar logs de la saga
docker-compose logs -f saga
```

### 3. Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it $(docker-compose ps -q postgres) psql -U postgres -d alpespartners_dijs

# Verificar tabla de saga logs
SELECT * FROM saga_logs ORDER BY fecha_procesamiento DESC LIMIT 5;

# Verificar que se crearon campaña y contrato
SELECT id, nombre FROM campanas ORDER BY fecha_creacion DESC LIMIT 3;
SELECT id, influencer_id, campana_id FROM contratos ORDER BY fecha_creacion DESC LIMIT 3;
```

## Archivos Modificados/Creados

### Nuevos Archivos
- `influencers/src/alpes_partners/modulos/sagas/infraestructura/consumidores.py`
- `influencers/run_saga.py`
- `SAGA_README.md`

### Archivos Modificados
- `docker-compose.yml` - Agregado servicio `saga`

### Archivos Existentes (No Modificados)
- `influencers/src/alpes_partners/modulos/sagas/aplicacion/coordinadores/saga_reservas.py` - Saga original
- `influencers/src/alpes_partners/modulos/sagas/infraestructura/repositorio_saga_log.py` - Repositorio
- `influencers/src/alpes_partners/modulos/sagas/dominio/` - Eventos y entidades

## Troubleshooting

### La saga no está procesando eventos

1. **Verificar que Pulsar esté funcionando**:
   ```bash
   curl http://localhost:8080/admin/v2/brokers/health
   ```

2. **Verificar logs de conexión**:
   ```bash
   docker-compose logs saga | grep "Conectando a Pulsar"
   ```

3. **Verificar suscripciones**:
   ```bash
   docker-compose logs saga | grep "Suscrito a eventos"
   ```

### Errores de base de datos

1. **Verificar que las tablas existan**:
   ```bash
   # Ejecutar migraciones si es necesario
   cd influencers/src/alpes_partners/modulos/sagas/infraestructura/
   python migraciones.py
   ```

### La saga procesa pero no ejecuta comandos

1. **Verificar handlers registrados**:
   ```bash
   docker-compose logs saga | grep "Handlers registrados"
   ```

2. **Verificar logs de comandos**:
   ```bash
   docker-compose logs saga | grep "ejecutar_commando"
   ```

## Puertos Utilizados

- **8084**: Saga Coordinator (health check)
- **8000**: Influencers
- **8001**: Campañas  
- **8002**: Contratos
- **6650**: Pulsar Client
- **8080**: Pulsar Admin (conflicto con microservicios, usar localhost:8080 solo para Pulsar)
- **5432**: PostgreSQL

La saga ahora debería escuchar y procesar correctamente todos los eventos de Pulsar.
