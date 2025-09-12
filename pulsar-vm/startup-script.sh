#!/bin/bash

# Script de inicio para VM con Docker y Pulsar
echo "🚀 Configurando Docker y Pulsar en VM..." > /var/log/pulsar-setup.log

# Actualizar sistema
apt-get update
apt-get install -y curl wget git

# Instalar Docker
echo "🐳 Instalando Docker..." >> /var/log/pulsar-setup.log
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Instalar Docker Compose
echo "🐙 Instalando Docker Compose..." >> /var/log/pulsar-setup.log
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Crear usuario para Docker
usermod -aG docker ubuntu

# Crear directorio para la aplicación
mkdir -p /opt/pulsar-app
cd /opt/pulsar-app

# Crear docker-compose.yml optimizado para VM (solo Pulsar y PostgreSQL)
cat > docker-compose.yml << 'EOF'
version: '3.8'

networks:
  app:
    driver: bridge

services:
  # Apache Pulsar Standalone
  pulsar:
    image: apachepulsar/pulsar:latest
    container_name: pulsar
    command: ["bin/pulsar", "standalone"]
    ports:
      - "6650:6650"  # Puerto para clientes Pulsar
      - "8080:8080"  # Puerto para la API REST de Pulsar
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/admin/v2/brokers/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - app
    volumes:
      - pulsar_data:/pulsar/data

volumes:
  pulsar_data:
EOF

# Crear script para gestionar los servicios
cat > manage-services.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Iniciando servicios de Pulsar..."
        docker-compose up -d
        echo "✅ Servicios iniciados"
        ;;
    stop)
        echo "🛑 Deteniendo servicios..."
        docker-compose down
        echo "✅ Servicios detenidos"
        ;;
    restart)
        echo "🔄 Reiniciando servicios..."
        docker-compose restart
        echo "✅ Servicios reiniciados"
        ;;
    status)
        echo "📊 Estado de los servicios:"
        docker-compose ps
        ;;
    logs)
        echo "📋 Logs de Pulsar:"
        docker-compose logs -f pulsar
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
EOF

chmod +x manage-services.sh

# Crear servicio systemd para auto-inicio
cat > /etc/systemd/system/pulsar-docker.service << 'EOF'
[Unit]
Description=Pulsar Docker Services
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/pulsar-app
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=root

[Install]
WantedBy=multi-user.target
EOF

# Habilitar el servicio
systemctl daemon-reload
systemctl enable pulsar-docker

# Iniciar Docker
systemctl start docker
systemctl enable docker

echo "⏳ Esperando que Docker esté listo..." >> /var/log/pulsar-setup.log
sleep 10

# Iniciar los servicios
echo "🚀 Iniciando servicios de Pulsar..." >> /var/log/pulsar-setup.log
docker-compose up -d

echo "⏳ Esperando que Pulsar esté listo..." >> /var/log/pulsar-setup.log
sleep 60

# Verificar estado
if docker ps | grep -q pulsar; then
    echo "✅ Pulsar está ejecutándose correctamente" >> /var/log/pulsar-setup.log
else
    echo "❌ Error: Pulsar no se pudo iniciar" >> /var/log/pulsar-setup.log
fi

# Mostrar información útil
echo "📋 Información de servicios:" >> /var/log/pulsar-setup.log
docker-compose ps >> /var/log/pulsar-setup.log

echo "✅ Configuración completada" >> /var/log/pulsar-setup.log
