"""Submódulo de Objetos de Transferencia de Datos (DTOs).

Contiene estructuras de datos desacopladas para entrada y salida de casos de uso.
"""

from app.application.dtos.alerta_dto import AlertaItemDto
from app.application.dtos.file_upload_dto import FileUploadDTO
from app.application.dtos.health_dto import (
    ExternalServiceHealthDTO,
    ExternalServicesHealthReportDTO,
)
from app.application.dtos.indice_empleabilidad_dto import (
    DimensionIndiceDTO,
    EvolucionIndicePuntoDTO,
    IndiceEmpleabilidadDTO,
    OcupacionRankingDTO,
)
from app.application.dtos.sync_dto import ExternalSyncResultDTO

__all__ = [
    "AlertaItemDto",
    "DimensionIndiceDTO",
    "EvolucionIndicePuntoDTO",
    "ExternalServiceHealthDTO",
    "ExternalServicesHealthReportDTO",
    "ExternalSyncResultDTO",
    "FileUploadDTO",
    "IndiceEmpleabilidadDTO",
    "OcupacionRankingDTO",
]
