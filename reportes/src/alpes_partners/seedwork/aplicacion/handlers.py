from abc import ABC, abstractmethod


class Handler(ABC):
    """Clase base para handlers."""
    
    @abstractmethod
    def handle(self, request):
        """Maneja una solicitud."""
        pass
