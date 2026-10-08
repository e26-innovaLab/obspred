"""Submódulo de Objetos de Transferencia de Datos (DTOs).

Contiene estructuras de datos desacopladas para entrada y salida de casos de uso.
"""

from app.application.dtos.file_upload_dto import FileUploadDTO
from app.application.dtos.indice_empleabilidad_dto import (
    DimensionIndiceDTO,
    EvolucionIndicePuntoDTO,
    IndiceEmpleabilidadDTO,
)

__all__ = [
    "DimensionIndiceDTO",
    "EvolucionIndicePuntoDTO",
    "FileUploadDTO",
    "IndiceEmpleabilidadDTO",
]
