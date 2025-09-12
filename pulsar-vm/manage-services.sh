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
