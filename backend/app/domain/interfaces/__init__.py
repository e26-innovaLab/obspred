"""Submódulo de interfaces y contratos abstractos (puertos) del dominio.

Define los protocolos que la infraestructura debe implementar (DIP).
"""

from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator

__all__ = ["IFileStorageService", "IFileValidator"]
