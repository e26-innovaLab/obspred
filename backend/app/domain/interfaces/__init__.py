"""Submódulo de interfaces y contratos abstractos (puertos) del dominio.

Define los protocolos que la infraestructura debe implementar (DIP).
"""

from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)

__all__ = [
    "IFileStorageService",
    "IFileValidator",
    "IIndiceEmpleabilidadRepository",
]
