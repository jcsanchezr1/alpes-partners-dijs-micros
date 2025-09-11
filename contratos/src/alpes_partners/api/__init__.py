import os

from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_swagger import swagger

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

def registrar_handlers():
    """Importa los módulos de aplicación para registrar handlers y comandos."""
    # La importación del módulo de aplicación registra automáticamente los comandos
    import alpes_partners.modulos.contratos.aplicacion

def importar_modelos_alchemy():
    """Importa los DTOs de SQLAlchemy para crear las tablas."""
    import alpes_partners.modulos.contratos.infraestructura.modelos

def comenzar_consumidor():
    """
    NOTA: Los consumidores de Pulsar se ejecutan en un servicio separado (pulsar-consumer)
    para evitar problemas de concurrencia y recursos en el proceso principal de Flask.
    
    Si necesitas ejecutar consumidores en el mismo proceso (no recomendado para producción),
    descomenta el código siguiente:
    """
    # import threading
    # import alpes_partners.modulos.contratos.infraestructura.consumidores as contratos
    # 
    # # Suscripción a eventos (solo para desarrollo/testing)
    # threading.Thread(target=contratos.suscribirse_a_eventos_contratos, daemon=True).start()
    # 
    # # Suscripción a comandos (solo para desarrollo/testing)  
    # threading.Thread(target=contratos.suscribirse_a_comandos_contratos, daemon=True).start()
    
    pass  # Los consumidores se ejecutan en el servicio pulsar-consumer

def create_app(configuracion={}):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración de base de datos
    from ..config.settings import settings
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = '9d58f98f-3ae8-4149-a09f-3a8c2012e32c'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['TESTING'] = configuracion.get('TESTING')

    # Inicializa la DB
    from ..seedwork.infraestructura.database import init_db_flask, init_db_flask_tables, db
    
    init_db_flask(app)
    importar_modelos_alchemy()
    registrar_handlers()

    with app.app_context():
        # Usar la función que crea las tablas con SQLAlchemy Core
        init_db_flask_tables()
        if not app.config.get('TESTING'):
            comenzar_consumidor()

    # Importa Blueprints
    from . import contratos

    # Registro de Blueprints
    app.register_blueprint(contratos.bp)

    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "AlpesPartners DIJS - API"
        return jsonify(swag)

    @app.route("/health")
    def health():
        return {"status": "up"}

    @app.route("/")
    def root():
        return {
            "mensaje": "AlpesPartners DIJS - API",
            "version": "1.0.0",
            "estado": "activo"
        }

    return app
