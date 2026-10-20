"""Submódulo de interfaces y contratos abstractos (puertos) del dominio.

Define los protocolos que la infraestructura debe implementar (DIP).
"""

from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)
from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator
from app.domain.interfaces.indicador_repository import IIndicadorRepository
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)

__all__ = [
    "IExternalDataConnector",
    "IFileStorageService",
    "IFileValidator",
    "IIndicadorRepository",
    "IIndiceEmpleabilidadRepository",
    "RawIndicatorRecord",
]
