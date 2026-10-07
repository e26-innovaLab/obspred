"""Entidad de dominio que representa un archivo cargado en el sistema."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class UploadedFile:
    """Entidad inmutable representativa de un archivo persistido para ingesta.

    Attributes:
        filename: Nombre unívoco asignado al archivo en almacenamiento.
        original_filename: Nombre provisto originalmente por el usuario.
        file_path: Ruta de ubicación del archivo en el sistema de almacenamiento.
        size_bytes: Tamaño en bytes del archivo.
        content_type: Tipo MIME del archivo.
        uploaded_at: Marca temporal UTC de persistencia del archivo.
    """

    filename: str
    original_filename: str
    file_path: Path
    size_bytes: int
    content_type: str = "text/csv"
    uploaded_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Valida las invariantes de la entidad tras su inicialización.

        Raises:
            ValueError: Si el tamaño es negativo o el nombre está vacío.
        """
        if self.size_bytes < 0:
            raise ValueError("El tamaño del archivo no puede ser negativo.")
        if not self.filename.strip():
            raise ValueError("El nombre del archivo no puede estar vacío.")

    @property
    def file_extension(self) -> str:
        """Obtiene la extensión normalizada del archivo en minúsculas."""
        return self.file_path.suffix.lower()
