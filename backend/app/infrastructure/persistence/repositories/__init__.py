"""Implementaciones concretas de repositorios de persistencia."""

from .indice_empleabilidad_repository import (
    SqlAlchemyIndiceEmpleabilidadRepository,
)

__all__ = ["SqlAlchemyIndiceEmpleabilidadRepository"]
