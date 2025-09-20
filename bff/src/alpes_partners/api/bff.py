"""
API endpoints para el BFF.
"""

import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
from ..modulos.bff.aplicacion.servicios import BFFService
from ..modulos.bff.aplicacion.dto import CrearInfluencerRequest, CrearInfluencerResponse, HealthResponse
from ..modulos.bff.aplicacion.servicios_streaming import servicio_streaming
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Crear instancia del servicio
bff_service = BFFService()


def crear_rutas(app: Flask):
    """Crea las rutas de la API."""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            response = HealthResponse(
                status="up",
                service="bff-microservice",
                version=settings.app_version
            )
            return jsonify(response.dict()), 200
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/influencers', methods=['POST'])
    def crear_influencer():
        """Endpoint para crear un influencer."""
        try:
            # Validar request
            if not request.is_json:
                return jsonify({"error": "Content-Type debe ser application/json"}), 400
            
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['id_influencer', 'nombre', 'email', 'categorias']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Campo requerido: {field}"}), 400
            
            # Crear request DTO
            request_dto = CrearInfluencerRequest(**data)
            
            # Procesar con el servicio
            result = bff_service.crear_influencer(
                id_influencer=request_dto.id_influencer,
                nombre=request_dto.nombre,
                email=request_dto.email,
                categorias=request_dto.categorias,
                plataformas=request_dto.plataformas,
                descripcion=request_dto.descripcion,
                biografia=request_dto.biografia,
                sitio_web=request_dto.sitio_web,
                telefono=request_dto.telefono
            )
            
            # Crear response
            response = CrearInfluencerResponse(**result)
            
            # Para operaciones asíncronas exitosas, devolver 202 (Accepted)
            status_code = 202 if result['success'] else 500
            return jsonify(response.dict()), status_code
            
        except Exception as e:
            logger.error(f"Error en crear influencer: {e}")
            return jsonify({
                "success": False,
                "message": f"Error interno del servidor: {str(e)}"
            }), 500
    
    @app.route('/stream', methods=['GET'])
    def stream_eventos():
        """Endpoint para streaming de eventos en tiempo real usando Server-Sent Events."""
        try:
            logger.info("Iniciando stream de eventos")
            
            def generar_respuesta():
                """Genera la respuesta de streaming."""
                try:
                    # Generar stream de eventos
                    for evento in servicio_streaming.generar_stream_eventos():
                        # Formatear como texto con "Nuevo evento" y JSON
                        data_json = jsonify(evento).get_data(as_text=True)
                        yield f"Nuevo evento\n{data_json}\n"
                        
                except GeneratorExit:
                    logger.info("Cliente desconectado")
                except Exception as e:
                    logger.error(f"Error en stream: {e}")
                    yield f"Error: {str(e)}\n"
            
            # Crear respuesta con headers SSE
            response = Response(
                stream_with_context(generar_respuesta()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Cache-Control'
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error en endpoint /stream: {e}")
            return jsonify({
                "error": "Error interno del servidor",
                "message": str(e)
            }), 500
    
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint."""
        return jsonify({
            "service": "bff-microservice",
            "version": settings.app_version,
            "endpoints": ["/health", "/influencers", "/stream"]
        }), 200
