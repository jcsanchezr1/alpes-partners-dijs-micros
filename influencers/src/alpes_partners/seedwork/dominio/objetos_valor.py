from abc import ABC
from typing import Any


class ObjetoValor(ABC):
    """Clase base para objetos valor."""
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __str__(self) -> str:
        attrs = ', '.join(f'{k}={v}' for k, v in self.__dict__.items())
        return f'{self.__class__.__name__}({attrs})'


class Email(ObjetoValor):
    """Objeto valor para email."""
    
    def __init__(self, valor: str) -> None:
        if not valor or '@' not in valor:
            raise ValueError("Email inválido")
        self.valor = valor.lower().strip()


class Telefono(ObjetoValor):
    """Objeto valor para teléfono."""
    
    def __init__(self, numero: str) -> None:
        # Remover espacios y caracteres especiales
        numero_limpio = ''.join(filter(str.isdigit, numero))
        if len(numero_limpio) < 7:
            raise ValueError("Teléfono inválido")
        self.numero = numero_limpio


class Dinero(ObjetoValor):
    """Objeto valor para representar dinero."""
    
    def __init__(self, cantidad: float, moneda: str = "USD") -> None:
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self.cantidad = round(cantidad, 2)
        self.moneda = moneda.upper()
    
    def __add__(self, other: 'Dinero') -> 'Dinero':
        if self.moneda != other.moneda:
            raise ValueError("No se pueden sumar monedas diferentes")
        return Dinero(self.cantidad + other.cantidad, self.moneda)
    
    def __sub__(self, other: 'Dinero') -> 'Dinero':
        if self.moneda != other.moneda:
            raise ValueError("No se pueden restar monedas diferentes")
        return Dinero(self.cantidad - other.cantidad, self.moneda)
