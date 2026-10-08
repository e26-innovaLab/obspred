"""Excepciones de dominio para la carga y almacenamiento de archivos."""

from app.domain.exceptions.base import DomainException


class InvalidFileExtensionException(DomainException):
    """Excepción lanzada si el archivo no tiene el formato permitido."""

    def __init__(self, filename: str, allowed_extension: str = ".csv") -> None:
        """Inicializa la excepción detallando el archivo y la extensión requerida.

        Args:
            filename: Nombre del archivo proporcionado.
            allowed_extension: Extensión requerida por la regla de negocio.
        """
        message = (
            f"El archivo '{filename}' no es válido. "
            f"Solo se admiten archivos con extensión '{allowed_extension}'."
        )
        super().__init__(message)
        self.filename = filename
        self.allowed_extension = allowed_extension


class EmptyFileException(DomainException):
    """Excepción lanzada cuando el archivo subido carece de contenido."""

    def __init__(self, filename: str) -> None:
        """Inicializa la excepción indicando el archivo vacío.

        Args:
            filename: Nombre del archivo recibido.
        """
        message = (
            f"El archivo '{filename}' está vacío. "
            "No se permite cargar archivos sin contenido."
        )
        super().__init__(message)
        self.filename = filename


class FileSizeExceededException(DomainException):
    """Excepción lanzada cuando el tamaño del archivo supera el límite configurado."""

    def __init__(self, filename: str, size_bytes: int, max_bytes: int) -> None:
        """Inicializa la excepción con el tamaño actual y el límite permitido.

        Args:
            filename: Nombre del archivo.
            size_bytes: Tamaño en bytes detectado.
            max_bytes: Tamaño máximo en bytes permitido.
        """
        max_mb = max_bytes / (1024 * 1024)
        current_mb = size_bytes / (1024 * 1024)
        message = (
            f"El archivo '{filename}' ({current_mb:.2f} MB) excede el tamaño máximo "
            f"permitido de {max_mb:.2f} MB."
        )
        super().__init__(message)
        self.filename = filename
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes


class InvalidFileContentException(DomainException):
    """Excepción lanzada si el archivo contiene datos binarios no legibles."""

    def __init__(self, filename: str, detail: str) -> None:
        """Inicializa la excepción indicando el defecto del contenido.

        Args:
            filename: Nombre del archivo procesado.
            detail: Detalle de la inconsistencia en el contenido.
        """
        message = (
            f"El contenido del archivo '{filename}' es inválido para formato CSV: "
            f"{detail}"
        )
        super().__init__(message)
        self.filename = filename
        self.detail = detail


class FileStorageException(DomainException):
    """Excepción lanzada cuando ocurre un error al persistir el archivo."""

    def __init__(self, filename: str, reason: str) -> None:
        """Inicializa la excepción indicando el fallo de almacenamiento.

        Args:
            filename: Nombre del archivo que no pudo ser persistido.
            reason: Causa o detalle del fallo.
        """
        message = f"No se pudo guardar el archivo '{filename}': {reason}"
        super().__init__(message)
        self.filename = filename
        self.reason = reason
