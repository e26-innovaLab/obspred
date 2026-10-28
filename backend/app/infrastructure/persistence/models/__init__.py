"""Modelos de datos relacionales basados en SQLAlchemy."""

from app.infrastructure.persistence.models.indicador import IndicadorModel
from app.infrastructure.persistence.models.brecha_model import HabilidadBrechaModel

__all__ = [
"IndicadorModel",
"HabilidadBrechaModel"
]
