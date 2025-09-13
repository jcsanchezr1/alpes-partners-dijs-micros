import logging
from .api import create_app
from .config.settings import settings

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configurar loggers específicos para nuestros módulos
logging.getLogger('alpes_partners').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)  # Para ver queries SQL

# Crear aplicación Flask
app = create_app()

if __name__ == "__main__":
    app.run(
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.debug
    )