"""
Handlers para comandos externos que se comunican con otros microservicios.
"""

import logging
import json
from typing import Dict, Any
from pydispatch import dispatcher

from ....seedwork.aplicacion.comandos import ejecutar_commando
from .comandos.comandos_externos import RegistrarCampana, CrearContrato

logger = logging.getLogger(__name__)


class HandlerComandosExternos:
    """Handler para comandos que deben ejecutarse en otros microservicios."""
    
    @staticmethod
    def handle_registrar_campana(comando: RegistrarCampana):
        """
        Manejar comando de registrar campaña enviándolo como evento de integración.
        En una implementación real, esto se enviaría a través de un message broker (Pulsar, Kafka, etc.)
        """
        logger.info(f"SAGA HANDLER: Procesando comando RegistrarCampana - {comando.nombre}")
        
        try:
            # Crear evento de integración para enviar al microservicio de campañas
            evento_crear_campana = {
                'tipo_evento': 'CrearCampanaRequerida',
                'datos': {
                    'fecha_creacion': comando.fecha_creacion,
                    'fecha_actualizacion': comando.fecha_actualizacion,
                    'id': comando.id,
                    'nombre': comando.nombre,
                    'descripcion': comando.descripcion,
                    'tipo_comision': comando.tipo_comision,
                    'valor_comision': comando.valor_comision,
                    'moneda': comando.moneda,
                    'fecha_inicio': comando.fecha_inicio,
                    'fecha_fin': comando.fecha_fin,
                    'titulo_material': comando.titulo_material,
                    'descripcion_material': comando.descripcion_material,
                    'categorias_objetivo': comando.categorias_objetivo,
                    'tipos_afiliado_permitidos': comando.tipos_afiliado_permitidos,
                    'paises_permitidos': comando.paises_permitidos,
                    'enlaces_material': comando.enlaces_material,
                    'imagenes_material': comando.imagenes_material,
                    'banners_material': comando.banners_material,
                    'metricas_minimas': comando.metricas_minimas,
                    'auto_activar': comando.auto_activar,
                    'influencer_origen_id': comando.influencer_origen_id,
                    'categoria_origen': comando.categoria_origen,
                    'influencer_origen_nombre': comando.influencer_origen_nombre,
                    'influencer_origen_email': comando.influencer_origen_email
                }
            }
            
            # En una implementación real, aquí enviarías el evento a través de Pulsar/Kafka
            # Por ahora, solo loggeamos que el comando sería enviado
            logger.info(f"SAGA HANDLER: Comando RegistrarCampana preparado para envío:")
            logger.info(f"  - ID Campaña: {comando.id}")
            logger.info(f"  - Nombre: {comando.nombre}")
            logger.info(f"  - Influencer: {comando.influencer_origen_nombre}")
            logger.info(f"SAGA HANDLER: [SIMULADO] Evento enviado al microservicio de campañas")
            
            # Simular respuesta exitosa
            return True
            
        except Exception as e:
            logger.error(f"SAGA HANDLER: Error procesando RegistrarCampana: {e}")
            raise
    
    @staticmethod
    def handle_crear_contrato(comando: CrearContrato):
        """
        Manejar comando de crear contrato enviándolo como evento de integración.
        """
        logger.info(f"SAGA HANDLER: Procesando comando CrearContrato - {comando.campana_nombre}")
        
        try:
            # Crear evento de integración para enviar al microservicio de contratos
            evento_crear_contrato = {
                'tipo_evento': 'CrearContratoRequerido',
                'datos': {
                    'fecha_creacion': comando.fecha_creacion,
                    'fecha_actualizacion': comando.fecha_actualizacion,
                    'id': comando.id,
                    'influencer_id': comando.influencer_id,
                    'influencer_nombre': comando.influencer_nombre,
                    'influencer_email': comando.influencer_email,
                    'campana_id': comando.campana_id,
                    'campana_nombre': comando.campana_nombre,
                    'categorias': comando.categorias,
                    'descripcion': comando.descripcion,
                    'monto_base': comando.monto_base,
                    'moneda': comando.moneda,
                    'fecha_inicio': comando.fecha_inicio,
                    'fecha_fin': comando.fecha_fin,
                    'entregables': comando.entregables,
                    'tipo_contrato': comando.tipo_contrato
                }
            }
            
            # En una implementación real, aquí enviarías el evento a través de Pulsar/Kafka
            logger.info(f"SAGA HANDLER: Comando CrearContrato preparado para envío:")
            logger.info(f"  - ID Contrato: {comando.id}")
            logger.info(f"  - Influencer: {comando.influencer_nombre}")
            logger.info(f"  - Campaña: {comando.campana_nombre}")
            logger.info(f"SAGA HANDLER: [SIMULADO] Evento enviado al microservicio de contratos")
            
            # Simular respuesta exitosa
            return True
            
        except Exception as e:
            logger.error(f"SAGA HANDLER: Error procesando CrearContrato: {e}")
            raise


# Registrar handlers para comandos externos usando el sistema de comandos
@ejecutar_commando.register(RegistrarCampana)
def ejecutar_comando_registrar_campana(comando: RegistrarCampana):
    """Ejecutar comando de registrar campaña."""
    handler = HandlerComandosExternos()
    return handler.handle_registrar_campana(comando)


@ejecutar_commando.register(CrearContrato)
def ejecutar_comando_crear_contrato(comando: CrearContrato):
    """Ejecutar comando de crear contrato."""
    handler = HandlerComandosExternos()
    return handler.handle_crear_contrato(comando)


logger.info("SAGA HANDLERS: Handlers de comandos externos registrados exitosamente")
