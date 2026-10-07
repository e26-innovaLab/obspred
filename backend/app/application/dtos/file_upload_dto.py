"""Objetos de Transferencia de Datos (DTO) para carga de archivos."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FileUploadDTO:
    """DTO representativo del resultado de almacenar un archivo subido.

    Attributes:
        filename: Nombre del archivo generado o almacenado.
        original_filename: Nombre original provisto por el usuario o cliente.
        file_path: Ruta relativa o absoluta de persistencia física del archivo.
        size_bytes: Cantidad de bytes almacenados.
        content_type: Tipo de medio MIME del archivo (opcional).
    """

    filename: str
    original_filename: str
    file_path: str
    size_bytes: int
    content_type: Optional[str] = None
