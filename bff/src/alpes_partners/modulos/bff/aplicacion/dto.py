"""
DTOs para el BFF.
"""

from pydantic import BaseModel, Field
from typing import List


class CrearInfluencerRequest(BaseModel):
    """Request para crear un influencer."""
    id_influencer: str = Field(..., description="ID único del influencer")
    nombre: str = Field(..., description="Nombre del influencer")
    email: str = Field(..., description="Email del influencer")
    categorias: List[str] = Field(..., description="Lista de categorías del influencer")
    plataformas: List[str] = Field(default=[], description="Lista de plataformas del influencer")
    descripcion: str = Field(default="", description="Descripción del influencer")
    biografia: str = Field(default="", description="Biografía del influencer")
    sitio_web: str = Field(default="", description="Sitio web del influencer")
    telefono: str = Field(default="", description="Teléfono del influencer")


class CrearInfluencerResponse(BaseModel):
    """Response del endpoint de crear influencer."""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo del resultado")


class HealthResponse(BaseModel):
    """Response del endpoint de health check."""
    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión del servicio")
