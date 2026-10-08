"""Implementaciones concretas de repositorios de persistencia."""

from app.infrastructure.persistence.repositories.indice_empleabilidad_repository import (
    SqlAlchemyIndiceEmpleabilidadRepository,
)

__all__ = ["SqlAlchemyIndiceEmpleabilidadRepository"]
