from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from functools import singledispatch
import uuid


class Comando:
    """Clase base para comandos."""
    ...


class ComandoIntegracion(Comando):
    """Comandos que cruzan límites de contexto."""
    pass


class ComandoHandler(ABC):
    """Handler base para comandos."""
    
    @abstractmethod
    def handle(self, comando: Comando):
        raise NotImplementedError()


@singledispatch
def ejecutar_commando(comando):
    """Ejecutor de comandos usando singledispatch."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"DISPATCHER: No hay implementación registrada para {type(comando).__name__}")
    logger.error(f"DISPATCHER: Comando recibido: {comando}")
    logger.error(f"DISPATCHER: Tipo del comando: {type(comando)}")
    logger.error(f"DISPATCHER: Registry actual: {ejecutar_commando.registry}")
    raise NotImplementedError(f'No existe implementación para el comando de tipo {type(comando).__name__}')
