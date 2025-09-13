#!/usr/bin/env python3
"""
Script independiente para enviar eventos de contrato creado a Pulsar.

Este script no depende del código del repositorio y usa directamente
la biblioteca de Pulsar para enviar eventos al tópico 'eventos-contratos'.
"""

import pulsar
import json
import time
import uuid
import datetime
import os
from pulsar.schema import Record, String, Float, Long, AvroSchema


# Definir esquemas directamente en el script
class ContratoCreadoPayload(Record):
    """Payload del evento de contrato creado."""
    id_contrato = String()
    id_influencer = String()
    id_campana = String()
    monto_total = Float()
    moneda = String()
    tipo_contrato = String()
    fecha_creacion = String()


# Esquema simplificado que coincide con lo que espera el tópico
class EventoContratoCreado(Record):
    """Evento simplificado que solo contiene el payload."""
    data = ContratoCreadoPayload()


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
        EventoContratoCreado: Evento listo para enviar
    """
    # Crear payload
    payload = ContratoCreadoPayload(
        id_contrato=str(datos_contrato['id_contrato']),
        id_influencer=str(datos_contrato['id_influencer']),
        id_campana=str(datos_contrato['id_campana']),
        monto_total=float(datos_contrato['monto_total']),
        moneda=str(datos_contrato['moneda']),
        tipo_contrato=str(datos_contrato['tipo_contrato']),
        fecha_creacion=str(datos_contrato['fecha_creacion'])
    )
    
    # Crear evento simplificado (solo con data)
    evento = EventoContratoCreado(data=payload)
    
    return evento


def enviar_evento_a_pulsar(evento, topico='eventos-contratos'):
    """
    Envía un evento a Pulsar.
    
    Args:
        evento: Evento a enviar
        topico: Nombre del tópico (por defecto 'eventos-contratos')
        
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
        schema = AvroSchema(EventoContratoCreado)
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
    print("📋 Resumen del Evento a Enviar:")
    print("-" * 40)
    print(f"   ID Contrato: {datos['id_contrato']}")
    print(f"   ID Influencer: {datos['id_influencer']}")
    print(f"   ID Campaña: {datos['id_campana']}")
    print(f"   Monto: {datos['monto_total']} {datos['moneda']}")
    print(f"   Tipo: {datos['tipo_contrato']}")
    print(f"   Fecha: {datos['fecha_creacion']}")
    print()


def main():
    """Función principal del script."""
    print("🚀 Envío de Evento de Contrato a Pulsar")
    print("=" * 50)
    
    # Datos del evento (los que proporcionaste)
    datos_evento = {
        'id_contrato': 'fdad3d32-f6ea-4836-bc11-bb622036ab7c',
        'id_influencer': 'inf-12345',
        'id_campana': 'camp-67890',
        'monto_total': 2500.0,
        'moneda': 'USD',
        'tipo_contrato': 'temporal',
        'fecha_creacion': '2025-09-13 01:07:56.578686'
    }
    
    # Mostrar configuración
    broker_host = obtener_broker_host()
    print(f"📍 Broker Pulsar: {broker_host}:6650")
    print(f"📨 Tópico destino: eventos-contratos")
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
            print("   El evento ha sido publicado en el tópico 'eventos-contratos'")
            print("   Los consumidores pueden procesarlo ahora.")
        else:
            print("\n💥 Error al enviar el evento")
            print("   Consejos para solucionar:")
            print("   - Verifica que Pulsar esté ejecutándose")
            print("   - Revisa la variable de entorno PULSAR_ADDRESS")
            print("   - Asegúrate de que tienes conectividad de red")
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
