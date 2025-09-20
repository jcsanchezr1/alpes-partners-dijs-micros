#!/usr/bin/env python3
"""
Script independiente para enviar eventos de crear influencer a Pulsar.

Este script no depende del código del repositorio y usa directamente
la biblioteca de Pulsar para enviar eventos al tópico 'eventos-crear-influencer'.
"""

import pulsar
import json
import time
import uuid
import datetime
import os
from pulsar.schema import Record, String, Array, AvroSchema


# Definir esquemas directamente en el script
class CrearInfluencerPayload(Record):
    """Payload del evento de crear influencer."""
    id = String()
    nombre = String()
    email = String()
    categorias = Array(String())  # Lista de categorías
    descripcion = String(default=None, required=False)
    biografia = String(default=None, required=False)
    sitio_web = String(default=None, required=False)
    telefono = String(default=None, required=False)
    fecha_creacion = String()  # ISO format datetime
    fecha_actualizacion = String()  # ISO format datetime


# Esquema simplificado que coincide con el patrón de reportes
class EventoCrearInfluencer(Record):
    """Evento de integración para crear influencer."""
    data = CrearInfluencerPayload()


def unix_time_millis(dt):
    """Convierte datetime a timestamp en milisegundos."""
    return int(dt.timestamp() * 1000)


def obtener_broker_host():
    """Obtiene la dirección del broker Pulsar."""
    return os.getenv('PULSAR_ADDRESS', 'localhost')


def crear_evento_integracion(datos_influencer):
    """
    Crea un evento de integración a partir de los datos del influencer.
    
    Args:
        datos_influencer: Diccionario con los datos del influencer
        
    Returns:
        EventoCrearInfluencer: Evento listo para enviar
    """
    # Generar ID único si no se proporciona
    influencer_id = datos_influencer.get('id', str(uuid.uuid4()))
    
    # Obtener fecha actual
    fecha_actual = datetime.datetime.utcnow().isoformat()
    
    # Generar IDs para el evento
    evento_id = str(uuid.uuid4())
    
    # Crear payload
    payload = CrearInfluencerPayload(
        id=influencer_id,
        nombre=str(datos_influencer['nombre']),
        email=str(datos_influencer['email']),
        categorias=list(datos_influencer.get('categorias', [])),
        descripcion=datos_influencer.get('descripcion'),
        biografia=datos_influencer.get('biografia'),
        sitio_web=datos_influencer.get('sitio_web'),
        telefono=datos_influencer.get('telefono'),
        fecha_creacion=datos_influencer.get('fecha_creacion', fecha_actual),
        fecha_actualizacion=datos_influencer.get('fecha_actualizacion', fecha_actual)
    )
    
    # Crear evento simplificado (solo con data)
    evento = EventoCrearInfluencer(data=payload)
    
    return evento


def enviar_evento_a_pulsar(evento, topico='eventos-crear-influencer'):
    """
    Envía un evento a Pulsar.
    
    Args:
        evento: Evento a enviar
        topico: Nombre del tópico (por defecto 'eventos-crear-influencer')
        
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    cliente = None
    try:
        # Crear cliente Pulsar
        broker_url = f'pulsar://{obtener_broker_host()}:6650'
        print(f"Conectando a Pulsar: {broker_url}")
        
        cliente = pulsar.Client(broker_url)
        
        # Crear productor con schema Avro
        schema = AvroSchema(EventoCrearInfluencer)
        productor = cliente.create_producer(topico, schema=schema)
        
        # Enviar mensaje
        print(f"Enviando evento al tópico '{topico}'...")
        productor.send(evento)
        
        print("Evento enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"Error al enviar evento: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
        
    finally:
        if cliente:
            cliente.close()


def mostrar_resumen_evento(datos):
    """Muestra un resumen del evento que se va a enviar."""
    print("📋 Resumen del Evento a Enviar:")
    print("-" * 40)
    print(f"   ID: {datos.get('id', 'Se generará automáticamente')}")
    print(f"   Nombre: {datos['nombre']}")
    print(f"   Email: {datos['email']}")
    print(f"   Categorías: {', '.join(datos.get('categorias', []))}")
    if datos.get('descripcion'):
        print(f"   Descripción: {datos['descripcion']}")
    if datos.get('biografia'):
        print(f"   Biografía: {datos['biografia']}")
    if datos.get('sitio_web'):
        print(f"   Sitio Web: {datos['sitio_web']}")
    if datos.get('telefono'):
        print(f"   Teléfono: {datos['telefono']}")
    print()


def generar_datos_fake_influencer():
    """Genera datos fake dinámicos para un influencer."""
    import random
    from datetime import datetime
    
    # Listas de datos fake
    nombres = [
        "Ana García"
    ]
    
    categorias_disponibles = [
        "moda", "belleza", "fitness", "viajes", "comida", "tecnología", "gaming", 
        "lifestyle", "arte", "música", "deportes", "educación", "salud", "negocios"
    ]
    
    dominios_email = [
        "gmail.com"
    ]
    
    # Generar datos aleatorios
    nombre_completo = random.choice(nombres)
    nombre_usuario = nombre_completo.lower().replace(" ", ".").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    numero_random = random.randint(1, 999)
    
    email = f"{nombre_usuario}@{random.choice(dominios_email)}"
    categorias_seleccionadas = random.sample(categorias_disponibles, random.randint(2, 4))
    
    return {
        "nombre": nombre_completo,
        "email": email,
        "categorias": categorias_seleccionadas,
        "descripcion": f"Influencer de {' y '.join(categorias_seleccionadas[:2])} con gran engagement",
        "biografia": f"Creador de contenido especializado en {categorias_seleccionadas[0]} con más de 50K seguidores",
        "sitio_web": f"https://{nombre_usuario.replace('.', '')}.com",
        "telefono": f"+34{random.randint(600000000, 699999999)}"
    }


def main():
    """Función principal del script."""
    print("Envío de Evento de Crear Influencer a Pulsar")
    print("=" * 55)
    
    # Generar datos dinámicos del influencer
    datos_evento = generar_datos_fake_influencer()
    
    # Mostrar configuración
    broker_host = obtener_broker_host()
    print(f"Broker Pulsar: {broker_host}:6650")
    print(f"Tópico destino: eventos-crear-influencer")
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
            print("\n¡Evento enviado exitosamente!")
            print("   El evento ha sido publicado en el tópico 'eventos-crear-influencer'")
            print("   El microservicio de influencers puede procesarlo ahora.")
        else:
            print("\n Error al enviar el evento")
            print("   Consejos para solucionar:")
            print("   - Verifica que Pulsar esté ejecutándose")
            print("   - Revisa la variable de entorno PULSAR_ADDRESS")
            print("   - Asegúrate de que tienes conectividad de red")
            print("   - Verifica que el microservicio de influencers esté ejecutándose")
            return 1
            
    except KeyboardInterrupt:
        print("\n Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n Error inesperado: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
