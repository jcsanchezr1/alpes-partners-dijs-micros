"""
API endpoints para el BFF.
"""

import logging
from flask import Flask, request, jsonify
from ..modulos.bff.aplicacion.servicios import BFFService
from ..modulos.bff.aplicacion.dto import CrearInfluencerRequest, CrearInfluencerResponse, HealthResponse
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
    
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint."""
        return jsonify({
            "service": "bff-microservice",
            "version": settings.app_version,
            "endpoints": ["/health", "/influencers"]
        }), 200
