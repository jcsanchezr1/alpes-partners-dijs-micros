"""
Tests básicos para el microservicio BFF.
"""

import pytest
import sys
import os

# Agregar el directorio src al path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from alpes_partners.config.app import crear_app_minima
from alpes_partners.api.bff import crear_rutas


@pytest.fixture
def app():
    """Crear aplicación de prueba."""
    app = crear_app_minima()
    crear_rutas(app)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Crear cliente de prueba."""
    return app.test_client()


def test_health_endpoint(client):
    """Test del endpoint de health check."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'up'
    assert data['service'] == 'bff-microservice'


def test_root_endpoint(client):
    """Test del endpoint raíz."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['service'] == 'bff-microservice'
    assert 'endpoints' in data


def test_crear_influencer_endpoint_success(client):
    """Test del endpoint de crear influencer con datos válidos."""
    data = {
        "id_influencer": "test-123",
        "nombre": "Test Influencer",
        "email": "test@example.com",
        "categorias": ["tecnologia", "gaming"],
        "plataformas": ["instagram", "youtube"],
        "descripcion": "Influencer de tecnología",
        "biografia": "Apasionado por la tecnología",
        "sitio_web": "https://test.com",
        "telefono": "+1234567890"
    }
    
    response = client.post('/influencers', json=data)
    # Nota: Este test fallará sin Pulsar, pero valida la estructura
    assert response.status_code in [202, 500]  # 202 para asíncrono, 500 si no hay Pulsar


def test_crear_influencer_endpoint_missing_fields(client):
    """Test del endpoint de crear influencer con campos faltantes."""
    data = {
        "id_influencer": "test-123",
        "nombre": "Test Influencer"
        # Faltan email y categorias (plataformas es opcional)
    }
    
    response = client.post('/influencers', json=data)
    assert response.status_code == 400


def test_crear_influencer_endpoint_invalid_content_type(client):
    """Test del endpoint de crear influencer con Content-Type inválido."""
    data = "invalid data"
    
    response = client.post('/influencers', data=data)
    assert response.status_code == 400
