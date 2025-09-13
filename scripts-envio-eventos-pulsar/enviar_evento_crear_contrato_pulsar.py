#!/usr/bin/env python3
"""
Script independiente para enviar eventos de crear contrato a Pulsar.

Este script no depende del código del repositorio y usa directamente
la biblioteca de Pulsar para enviar eventos al tópico 'eventos-campanas'.
"""

import pulsar
import json
import time
import uuid
import datetime
import os
from pulsar.schema import Record, String, Array, Float, AvroSchema


# Definir esquemas directamente en el script - Compatible con campañas
class CampanaCreadaPayload(Record):
    """Payload del evento de campaña creada."""
    campana_id = String()
    nombre = String()
    descripcion = String()
    tipo_comision = String()
    valor_comision = Float()
    moneda = String(default="USD")
    categorias_objetivo = Array(String())  # Lista de categorías objetivo
    fecha_inicio = String()  # ISO format datetime
    fecha_fin = String(default=None, required=False)  # ISO format datetime
    # Campos adicionales para crear contratos
    influencer_id = String(default=None, required=False)
    influencer_nombre = String(default=None, required=False)
    influencer_email = String(default=None, required=False)
    monto_base = Float(default=None, required=False)
    entregables = String(default=None, required=False)
    tipo_contrato = String(default="puntual")
    fecha_creacion = String()  # ISO format datetime


# Esquema simplificado que coincide con el patrón de reportes
class EventoCampanaCreada(Record):
    """Evento de integración para campaña creada."""
    data = CampanaCreadaPayload()


def unix_time_millis(dt):
    """Convierte datetime a timestamp en milisegundos."""
    return int(dt.timestamp() * 1000)


def obtener_broker_host():
    """Obtiene la dirección del broker Pulsar."""
    return os.getenv('PULSAR_ADDRESS', 'localhost')


def crear_evento_integracion(datos_contrato):
    """
    Crea un evento de integración a partir de los datos del contrato.
    
    Args:
        datos_contrato: Diccionario con los datos del contrato
        
    Returns:
        EventoCampanaCreada: Evento listo para enviar
    """
    # Obtener fecha actual
    fecha_actual = datetime.datetime.utcnow().isoformat()
    
    # Crear payload
    payload = CampanaCreadaPayload(
        campana_id=str(datos_contrato['campana_id']),
        nombre=str(datos_contrato['campana_nombre']),
        descripcion=str(datos_contrato['descripcion']),
        tipo_comision="cpa",  # Valor por defecto
        valor_comision=float(datos_contrato['monto_base']),
        moneda=str(datos_contrato.get('moneda', 'USD')),
        categorias_objetivo=list(datos_contrato.get('categorias', [])),
        fecha_inicio=datos_contrato.get('fecha_inicio', fecha_actual),
        fecha_fin=datos_contrato.get('fecha_fin'),
        # Campos adicionales para crear contratos
        influencer_id=str(datos_contrato['influencer_id']),
        influencer_nombre=str(datos_contrato['influencer_nombre']),
        influencer_email=str(datos_contrato['influencer_email']),
        monto_base=float(datos_contrato['monto_base']),
        entregables=datos_contrato.get('entregables'),
        tipo_contrato=str(datos_contrato.get('tipo_contrato', 'puntual')),
        fecha_creacion=datos_contrato.get('fecha_creacion', fecha_actual)
    )
    
    # Crear evento simplificado (solo con data)
    evento = EventoCampanaCreada(data=payload)
    
    return evento


def enviar_evento_a_pulsar(evento, topico='eventos-campanas'):
    """
    Envía un evento a Pulsar.
    
    Args:
        evento: Evento a enviar
        topico: Nombre del tópico (por defecto 'eventos-campanas')
        
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    cliente = None
    try:
        # Crear cliente Pulsar
        broker_url = f'pulsar://{obtener_broker_host()}:6650'
        print(f"🔗 Conectando a Pulsar: {broker_url}")
        
        cliente = pulsar.Client(broker_url)
        
        # Crear productor con schema Avro
        schema = AvroSchema(EventoCampanaCreada)
        productor = cliente.create_producer(topico, schema=schema)
        
        # Enviar mensaje
        print(f"📤 Enviando evento al tópico '{topico}'...")
        productor.send(evento)
        
        print("✅ Evento enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar evento: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
        
    finally:
        if cliente:
            cliente.close()


def mostrar_resumen_evento(datos):
    """Muestra un resumen del evento que se va a enviar."""
    print("📋 Resumen del Evento de Contrato a Enviar:")
    print("-" * 50)
    print(f"   Campaña ID: {datos['campana_id']}")
    print(f"   Campaña: {datos['campana_nombre']}")
    print(f"   Influencer ID: {datos['influencer_id']}")
    print(f"   Influencer: {datos['influencer_nombre']}")
    print(f"   Email: {datos['influencer_email']}")
    print(f"   Categorías: {', '.join(datos.get('categorias', []))}")
    print(f"   Descripción: {datos['descripcion']}")
    print(f"   Monto: {datos['monto_base']} {datos.get('moneda', 'USD')}")
    if datos.get('fecha_inicio'):
        print(f"   Fecha Inicio: {datos['fecha_inicio']}")
    if datos.get('fecha_fin'):
        print(f"   Fecha Fin: {datos['fecha_fin']}")
    if datos.get('entregables'):
        print(f"   Entregables: {datos['entregables']}")
    print(f"   Tipo Contrato: {datos.get('tipo_contrato', 'puntual')}")
    print()


def main():
    """Función principal del script."""
    print("🚀 Envío de Evento de Crear Contrato a Pulsar")
    print("=" * 60)
    
    # Datos del evento (los que proporcionaste)
    datos_evento = {
        "influencer_id": "inf-12345",
        "influencer_nombre": "Ana García",
        "influencer_email": "ana.garcia@example.com",
        "campana_id": "camp-67890",
        "campana_nombre": "Campaña Verano 2024",
        "categorias": ["moda", "lifestyle", "belleza"],
        "descripcion": "Contrato para promoción de productos de verano en redes sociales",
        "monto_base": 2500.0,
        "moneda": "USD",
        "fecha_inicio": "2024-06-01T00:00:00",
        "fecha_fin": "2024-08-31T23:59:59",
        "entregables": "5 posts en Instagram, 3 stories por semana, 1 reel mensual",
        "tipo_contrato": "temporal"
    }
    
    # Mostrar configuración
    broker_host = obtener_broker_host()
    print(f"📍 Broker Pulsar: {broker_host}:6650")
    print(f"📨 Tópico destino: eventos-campanas")
    print()
    
    # Mostrar resumen del evento
    mostrar_resumen_evento(datos_evento)
    
    try:
        # Crear evento de integración
        print("🔧 Creando evento de integración...")
        evento = crear_evento_integracion(datos_evento)
        
        # Enviar evento
        exito = enviar_evento_a_pulsar(evento)
        
        if exito:
            print("\n🎉 ¡Evento enviado exitosamente!")
            print("   El evento ha sido publicado en el tópico 'eventos-campanas'")
            print("   El microservicio de contratos puede procesarlo ahora.")
        else:
            print("\n💥 Error al enviar el evento")
            print("   Consejos para solucionar:")
            print("   - Verifica que Pulsar esté ejecutándose")
            print("   - Revisa la variable de entorno PULSAR_ADDRESS")
            print("   - Asegúrate de que tienes conectividad de red")
            print("   - Verifica que el microservicio de contratos esté ejecutándose")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
