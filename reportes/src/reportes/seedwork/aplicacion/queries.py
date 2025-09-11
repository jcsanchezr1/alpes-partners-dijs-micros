from abc import ABC, abstractmethod


class Query:
    """Clase base para queries."""
    pass


class QueryHandler(ABC):
    """Handler base para queries."""
    
    @abstractmethod
    def handle(self, query: Query):
        """Maneja una query."""
        raise NotImplementedError()
