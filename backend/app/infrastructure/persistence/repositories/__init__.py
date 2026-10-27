"""Implementaciones concretas de repositorios de persistencia."""

from .indicador_repository import SqlAlchemyIndicadorRepository
from .indice_empleabilidad_repository import (
    SqlAlchemyIndiceEmpleabilidadRepository,
)

__all__ = [
    "SqlAlchemyIndicadorRepository",
    "SqlAlchemyIndiceEmpleabilidadRepository",
]
