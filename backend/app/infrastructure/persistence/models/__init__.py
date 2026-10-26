"""Modelos de datos relacionales basados en SQLAlchemy."""

from app.infrastructure.persistence.models.indicador import IndicadorModel
from app.infrastructure.persistence.models.fuente import FuenteModel

__all__ = [
    "IndicadorModel",
    "FuenteModel",]
