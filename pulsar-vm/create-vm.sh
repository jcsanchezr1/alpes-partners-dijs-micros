#!/bin/bash

# Script para crear VM con Docker y Pulsar
echo "🚀 Creando VM con Docker y Pulsar en Compute Engine..."

# Configurar variables
PROJECT_ID=${1:-"tu-project-id"}
ZONE="us-central1-a"
VM_NAME="pulsar-docker-vm"
MACHINE_TYPE="e2-standard-2"
DISK_SIZE="10GB"

echo "📋 Configuración:"
echo "- Proyecto: $PROJECT_ID"
echo "- Zona: $ZONE"
echo "- VM: $VM_NAME"
echo "- Tipo: $MACHINE_TYPE"
echo "- Disco: $DISK_SIZE"

# Verificar que se proporcionó PROJECT_ID
if [ "$PROJECT_ID" = "tu-project-id" ]; then
    echo "❌ Error: Debes proporcionar tu PROJECT_ID"
    echo "Uso: $0 <PROJECT_ID>"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Verificar si la VM ya existe
if gcloud compute instances describe $VM_NAME --zone=$ZONE &>/dev/null; then
    echo "⚠️  La VM '$VM_NAME' ya existe. ¿Deseas eliminarla y crear una nueva? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🗑️  Eliminando VM existente..."
        gcloud compute instances delete $VM_NAME --zone=$ZONE --quiet
        sleep 10
    else
        echo "❌ Operación cancelada"
        exit 1
    fi
fi

# Crear VM con script de inicio
echo "🔨 Creando VM..."
if gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=pulsar-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=environment=development,service=pulsar \
    --reservation-affinity=any \
    --metadata-from-file startup-script=startup-script.sh; then
    echo "✅ VM creada exitosamente"
else
    echo "❌ Error al crear la VM"
    exit 1
fi

# Crear reglas de firewall (si no existe)
echo "🔥 Configurando firewall..."
if ! gcloud compute firewall-rules describe allow-pulsar &>/dev/null; then
    gcloud compute firewall-rules create allow-pulsar \
        --allow tcp:6650,tcp:8080,tcp:5432 \
        --source-ranges 0.0.0.0/0 \
        --target-tags pulsar-server \
        --description "Allow Pulsar and PostgreSQL traffic"
    echo "✅ Regla de firewall creada"
else
    echo "✅ Regla de firewall ya existe"
fi

# Obtener IP externa
echo "⏳ Esperando que la VM esté lista..."
sleep 30

# Intentar obtener IP externa con reintentos
for i in {1..5}; do
    EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null)
    if [ ! -z "$EXTERNAL_IP" ]; then
        break
    fi
    echo "🔄 Intento $i/5 - esperando IP externa..."
    sleep 10
done

if [ -z "$EXTERNAL_IP" ]; then
    echo "❌ Error: No se pudo obtener la IP externa de la VM"
    exit 1
fi

echo ""
echo "🎉 ¡VM creada exitosamente!"
echo "=========================="
echo "📡 IP Externa: $EXTERNAL_IP"
echo "🌐 Pulsar Admin URL: http://$EXTERNAL_IP:8080"
echo "🔗 Pulsar Broker URL: pulsar://$EXTERNAL_IP:6650"
echo "🗄️  PostgreSQL: $EXTERNAL_IP:5432"
echo ""
echo "📝 Comandos útiles:"
echo "# Conectar por SSH:"
echo "gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "# Ver logs de configuración:"
echo "gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo tail -f /var/log/pulsar-setup.log'"
echo ""
echo "# Gestionar servicios en la VM:"
echo "gcloud compute ssh $VM_NAME --zone=$ZONE --command='cd /opt/pulsar-app && sudo ./manage-services.sh status'"
echo ""
echo "📝 Para conectar tus servicios locales:"
echo "export PULSAR_ADDRESS_EXTERNAL=pulsar://$EXTERNAL_IP:6650"
echo "docker-compose -f docker-compose-external-pulsar.yml up -d"
echo ""
echo "⏳ La VM tardará ~3-5 minutos en estar completamente lista."
echo "   Puedes verificar el estado con los comandos de arriba."
