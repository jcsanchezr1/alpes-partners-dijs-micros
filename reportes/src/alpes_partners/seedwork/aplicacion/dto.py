from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class DTO(BaseModel, ABC):
    """Clase base para Data Transfer Objects."""
    
    class Config:
        from_attributes = True
        validate_assignment = True
        use_enum_values = True
