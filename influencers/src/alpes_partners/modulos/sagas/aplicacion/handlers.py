"""
Handlers para comandos externos que se comunican con otros microservicios.
"""

import logging
import json
from typing import Dict, Any
from pydispatch import dispatcher
from pulsar.schema import AvroSchema

from ....seedwork.aplicacion.comandos import ejecutar_commando
from .comandos.comandos_externos import RegistrarCampana, CrearContrato, EliminarCampana

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
            
            # Importar despachador para enviar comando real
            from ..infraestructura.despachadores import DespachadorCampanas
            from ..infraestructura.schema.v1.comandos import ComandoCrearCampana, CrearCampanaPayload
            import uuid
            from datetime import datetime
            
            # Convertir metricas_minimas de dict a string JSON
            import json
            metricas_minimas_str = json.dumps(comando.metricas_minimas) if comando.metricas_minimas else "{}"
            
            # Crear payload del comando
            payload = CrearCampanaPayload(
                fecha_creacion=comando.fecha_creacion,
                fecha_actualizacion=comando.fecha_actualizacion,
                id=comando.id,
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                tipo_comision=comando.tipo_comision,
                valor_comision=comando.valor_comision,
                moneda=comando.moneda,
                fecha_inicio=comando.fecha_inicio,
                fecha_fin=comando.fecha_fin,
                titulo_material=comando.titulo_material,
                descripcion_material=comando.descripcion_material,
                categorias_objetivo=comando.categorias_objetivo,
                tipos_afiliado_permitidos=comando.tipos_afiliado_permitidos,
                paises_permitidos=comando.paises_permitidos,
                enlaces_material=comando.enlaces_material,
                imagenes_material=comando.imagenes_material,
                banners_material=comando.banners_material,
                metricas_minimas=metricas_minimas_str,
                auto_activar=comando.auto_activar,
                influencer_origen_id=comando.influencer_origen_id,
                categoria_origen=comando.categoria_origen,
                influencer_origen_nombre=comando.influencer_origen_nombre,
                influencer_origen_email=comando.influencer_origen_email
            )
            
            # Crear evento de integración
            evento = ComandoCrearCampana(
                id=str(uuid.uuid4()),
                time=datetime.utcnow(),
                ingestion=datetime.utcnow(),
                specversion="v1",
                type="CrearCampanaRequerida",
                datacontenttype="AVRO",
                service_name="saga",
                data=payload
            )
            
            logger.info(f"SAGA HANDLER: Comando RegistrarCampana preparado para envío:")
            logger.info(f"  - ID Campaña: {comando.id}")
            logger.info(f"  - Nombre: {comando.nombre}")
            logger.info(f"  - Influencer: {comando.influencer_origen_nombre}")
            
            # Enviar comando real al microservicio de campañas
            despachador = DespachadorCampanas()
            despachador.publicar_comando_crear_campana(comando, "comandos-campanas")
            
            logger.info(f"SAGA HANDLER: Comando enviado al microservicio de campañas")
            
            # NO retornar True aquí - el saga debe esperar la respuesta del microservicio
            # El saga continuará cuando reciba el evento de respuesta (éxito o error)
            
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
            # Importar aquí para evitar dependencias circulares
            from ..infraestructura.despachadores import DespachadorContratos
            
            logger.info(f"SAGA HANDLER: Comando CrearContrato preparado para envío:")
            logger.info(f"  - ID Contrato: {comando.id}")
            logger.info(f"  - Influencer: {comando.influencer_nombre}")
            logger.info(f"  - Campaña: {comando.campana_nombre}")
            
            # Enviar comando real al microservicio de contratos
            despachador = DespachadorContratos()
            despachador.publicar_comando_crear_contrato(comando, "comandos-contratos-v2")
            
            logger.info(f"SAGA HANDLER: Comando enviado al microservicio de contratos")
            
            # NO retornar True aquí - el saga debe esperar la respuesta del microservicio
            # El saga continuará cuando reciba el evento de respuesta (éxito o error)
            
        except Exception as e:
            logger.error(f"SAGA HANDLER: Error procesando CrearContrato: {e}")
            raise

    @staticmethod
    def handle_eliminar_campana(comando: EliminarCampana):
        """
        Manejar comando de eliminar campaña (compensación).
        Publica un evento de integración para solicitar eliminación de campaña.
        """
        logger.info(f"SAGA HANDLER: Procesando comando EliminarCampana - Campaña: {comando.campana_id}")
        logger.info(f"SAGA HANDLER: Razón: {comando.razon}")
        
        try:
            # Importar aquí para evitar dependencias circulares
            from ..infraestructura.despachadores import DespachadorCampanas
            from ..dominio.eventos import CampanaEliminacionRequerida
            
            # Crear evento de integración
            evento_eliminacion = CampanaEliminacionRequerida(
                campana_id=comando.campana_id,
                influencer_id=comando.influencer_id,
                razon=comando.razon
            )
            
            logger.info(f"SAGA HANDLER: Evento de eliminación preparado:")
            logger.info(f"  - ID Campaña: {comando.campana_id}")
            logger.info(f"  - Influencer: {comando.influencer_id}")
            logger.info(f"  - Razón: {comando.razon}")
            
            # Publicar evento de integración
            despachador = DespachadorCampanas()
            despachador.publicar_evento_eliminacion_campana(evento_eliminacion)
            
            logger.info(f"SAGA HANDLER: Evento de eliminación publicado - Microservicio de campañas procesará la solicitud")
            logger.info(f"SAGA HANDLER: Compensación completada - Razón: {comando.razon}")
            
            return True
            
        except Exception as e:
            logger.error(f"SAGA HANDLER: Error procesando EliminarCampana: {e}")
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


@ejecutar_commando.register(EliminarCampana)
def ejecutar_comando_eliminar_campana(comando: EliminarCampana):
    """Ejecutar comando de eliminar campaña (compensación)."""
    handler = HandlerComandosExternos()
    return handler.handle_eliminar_campana(comando)


logger.info("SAGA HANDLERS: Handlers de comandos externos registrados exitosamente")
