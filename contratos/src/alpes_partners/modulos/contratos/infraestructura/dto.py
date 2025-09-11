"""DTOs para la capa de infraestructura del dominio de contratos

En este archivo usted encontrará los DTOs (modelos anémicos) de
la infraestructura del dominio de contratos

"""

# Importar los modelos existentes para Flask-SQLAlchemy
from .modelos import Base, ContratoModelo

# Re-exportar para compatibilidad con Flask
Contrato = ContratoModelo
