"""
Consumidor de comandos para el módulo de campanas.
Se suscribe a comandos de la saga y ejecuta comandos para crear campanas.
"""

import logging
import time
import json
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Imports esenciales
import pulsar
import _pulsar
from pulsar.schema import AvroSchema

from alpes_partners.config.app import crear_app_minima
from alpes_partners.seedwork.infraestructura import utils
from alpes_partners.modulos.campanas.infraestructura.schema.comandos import ComandoCrearCampana
from alpes_partners.modulos.campanas.aplicacion.comandos.crear_campana import RegistrarCampana, ejecutar_comando_registrar_campana

# Crear instancia de aplicación Flask para el contexto
app = crear_app_minima()


def suscribirse_a_comandos_campanas():
    """
    Suscribirse a comandos de campañas desde la saga.
    """
    cliente = None
    try:
        logger.info("CAMPANAS COMANDOS: Conectando a Pulsar...")
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        
        # Consumidor para comandos de campañas
        consumidor = cliente.subscribe(
            'comandos-campanas', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='campanas-sub-comandos', 
            schema=AvroSchema(ComandoCrearCampana)
        )

        logger.info("CAMPANAS COMANDOS: Suscrito a comandos de campañas")
        logger.info("CAMPANAS COMANDOS: Esperando comandos...")
        
        while True:
            try:
                mensaje = consumidor.receive()
                logger.info(f"CAMPANAS COMANDOS: Comando recibido - {mensaje.value()}")
                
                # Procesar comando
                _procesar_comando_campana(mensaje.value())
                
                # Confirmar procesamiento
                consumidor.acknowledge(mensaje)
                logger.info("CAMPANAS COMANDOS: Comando procesado y confirmado")
                
            except Exception as e:
                logger.error(f"CAMPANAS COMANDOS: Error procesando comando: {e}")
                time.sleep(5)  # Esperar antes de continuar
                
    except Exception as e:
        logger.error(f"CAMPANAS COMANDOS: Error en consumidor: {e}")
    finally:
        if cliente:
            cliente.close()


def _procesar_comando_campana(comando_pulsar):
    """
    Procesa un comando de crear campaña desde la saga.
    """
    with app.app_context():
        try:
            logger.info("CAMPANAS COMANDOS: Procesando comando de crear campaña")
            
            # Extraer datos del comando
            data = comando_pulsar.data
            logger.info(f"CAMPANAS COMANDOS: Datos del comando: {data}")
            
            # Convertir metricas_minimas de string a dict
            metricas_minimas = {}
            if data.metricas_minimas:
                try:
                    metricas_minimas = json.loads(data.metricas_minimas)
                except json.JSONDecodeError:
                    logger.warning(f"CAMPANAS COMANDOS: Error parseando metricas_minimas: {data.metricas_minimas}")
                    metricas_minimas = {}
            
            # Crear comando de dominio
            comando = RegistrarCampana(
                fecha_creacion=data.fecha_creacion,
                fecha_actualizacion=data.fecha_actualizacion,
                id=data.id,
                nombre=data.nombre,
                descripcion=data.descripcion,
                tipo_comision=data.tipo_comision,
                valor_comision=data.valor_comision,
                moneda=data.moneda,
                fecha_inicio=data.fecha_inicio,
                fecha_fin=data.fecha_fin,
                titulo_material=data.titulo_material,
                descripcion_material=data.descripcion_material,
                categorias_objetivo=list(data.categorias_objetivo) if data.categorias_objetivo else [],
                tipos_afiliado_permitidos=list(data.tipos_afiliado_permitidos) if data.tipos_afiliado_permitidos else [],
                paises_permitidos=list(data.paises_permitidos) if data.paises_permitidos else [],
                enlaces_material=list(data.enlaces_material) if data.enlaces_material else [],
                imagenes_material=list(data.imagenes_material) if data.imagenes_material else [],
                banners_material=list(data.banners_material) if data.banners_material else [],
                metricas_minimas=metricas_minimas,
                auto_activar=data.auto_activar,
                influencer_origen_id=data.influencer_origen_id,
                categoria_origen=data.categoria_origen,
                influencer_origen_nombre=data.influencer_origen_nombre,
                influencer_origen_email=data.influencer_origen_email
            )
            
            logger.info(f"CAMPANAS COMANDOS: Comando de dominio creado:")
            logger.info(f"  - ID: {comando.id}")
            logger.info(f"  - Nombre: {comando.nombre}")
            logger.info(f"  - Influencer: {comando.influencer_origen_nombre}")
            
            # Ejecutar comando de dominio
            ejecutar_comando_registrar_campana(comando)
            
            logger.info(f"CAMPANAS COMANDOS: Campaña creada exitosamente - ID: {comando.id}")
            
        except Exception as e:
            logger.error(f"CAMPANAS COMANDOS: Error procesando comando: {e}")
            import traceback
            logger.error(f"CAMPANAS COMANDOS: Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    suscribirse_a_comandos_campanas()
