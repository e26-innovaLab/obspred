"""Validador especializado para archivos tabulares en formato CSV."""

from pathlib import Path

from app.core.constants import CSV_FILE_EXTENSION, DEFAULT_MAX_UPLOAD_SIZE_BYTES
from app.domain.exceptions.file_upload import (
    EmptyFileException,
    FileSizeExceededException,
    InvalidFileContentException,
    InvalidFileExtensionException,
)
from app.domain.interfaces.file_validator import IFileValidator


class CsvFileValidator(IFileValidator):
    """Validador de reglas de negocio para archivos CSV (SRP y OCP).

    Attributes:
        max_size_bytes: Tamaño máximo permitido en bytes.
    """

    def __init__(
        self,
        max_size_bytes: int = DEFAULT_MAX_UPLOAD_SIZE_BYTES,
    ) -> None:
        """Inicializa el validador configurando los límites aceptables.

        Args:
            max_size_bytes: Límite superior en bytes para el archivo.
        """
        self.max_size_bytes = max_size_bytes

    def validate(self, filename: str, content: bytes) -> None:
        """Aplica las reglas de negocio sobre el archivo antes de su persistencia.

        Args:
            filename: Nombre original provisto del archivo.
            content: Contenido binario del archivo.

        Raises:
            InvalidFileExtensionException: Si el nombre o extensión no es .csv.
            EmptyFileException: Si el archivo está vacío o con solo espacios.
            FileSizeExceededException: Si el tamaño supera max_size_bytes.
            InvalidFileContentException: Si contiene bytes nulos o no es texto plano.
        """
        if not filename or not filename.strip():
            raise InvalidFileExtensionException(
                filename="desconocido",
                allowed_extension=CSV_FILE_EXTENSION,
            )

        clean_filename = Path(filename.strip()).name

        if not clean_filename.lower().endswith(CSV_FILE_EXTENSION):
            raise InvalidFileExtensionException(
                filename=clean_filename,
                allowed_extension=CSV_FILE_EXTENSION,
            )

        # Validación de contenido no vacío
        if not content or len(content.strip()) == 0:
            raise EmptyFileException(filename=clean_filename)

        # Validación de tamaño máximo permitido
        if len(content) > self.max_size_bytes:
            raise FileSizeExceededException(
                filename=clean_filename,
                size_bytes=len(content),
                max_bytes=self.max_size_bytes,
            )

        # Validación de contenido textual (detección de ejecutables o binarios)
        if b"\x00" in content[:4096]:
            raise InvalidFileContentException(
                filename=clean_filename,
                detail="El archivo contiene secuencias binarias no admitidas.",
            )

        # Validación de decodificación en codificaciones de texto estándar
        try:
            content[:4096].decode("utf-8")
        except UnicodeDecodeError:
            try:
                content[:4096].decode("latin-1")
            except UnicodeDecodeError as exc:
                raise InvalidFileContentException(
                    filename=clean_filename,
                    detail="Codificación incompatible con texto UTF-8 o Latin-1.",
                ) from exc
