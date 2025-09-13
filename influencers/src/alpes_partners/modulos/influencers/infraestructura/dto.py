"""DTOs para la capa de infraestructura del dominio de influencers

En este archivo usted encontrará los DTOs (modelos anémicos) de
la infraestructura del dominio de influencers

"""

# Importar los modelos existentes para Flask-SQLAlchemy
from .modelos import Base, InfluencerModelo

# Re-exportar para compatibilidad con Flask
Influencer = InfluencerModelo
