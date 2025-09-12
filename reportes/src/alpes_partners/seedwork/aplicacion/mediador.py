from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class Mediador(ABC):
    """Mediador para manejar comandos y queries."""
    
    @abstractmethod
    def publicar_comando(self, comando, **kwargs):
        """Publica un comando."""
        pass
    
    @abstractmethod
    def publicar_query(self, query, **kwargs):
        """Publica una query."""
        pass
