"""Servicio de aplicación para coordinar validación y guardado de CSV."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.application.dtos.file_upload_dto import FileUploadDTO
from app.core.constants import DEFAULT_CSV_CONTENT_TYPE
from app.domain.entities.uploaded_file import UploadedFile
from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator


class FileUploadService:
    """Caso de uso y servicio de aplicación para procesar subidas de CSV.

    Aplica las reglas de negocio de validación mediante el validador inyectado
    y delega la persistencia al servicio de almacenamiento (DIP).
    """

    def __init__(
        self,
        storage_service: IFileStorageService,
        validator: IFileValidator,
    ) -> None:
        """Inicializa el servicio inyectando sus dependencias de abstracción.

        Args:
            storage_service: Proveedor que implementa IFileStorageService.
            validator: Validador de reglas de negocio que implementa IFileValidator.
        """
        self.storage_service = storage_service
        self.validator = validator

    async def upload_csv(
        self,
        filename: str,
        content: bytes,
        content_type: Optional[str] = None,
    ) -> FileUploadDTO:
        """Valida que el archivo cumpla las reglas de negocio y lo persiste.

        Args:
            filename: Nombre original provisto del archivo.
            content: Contenido binario del archivo.
            content_type: Tipo MIME opcional informado por el cliente.

        Returns:
            FileUploadDTO: Metadatos del archivo persistido.

        Raises:
            DomainException: Si el validador detecta inconsistencias.
            FileStorageException: Si ocurre un error en la capa de persistencia.
        """
        # Ejecución del validador de dominio desacoplado (SRP / OCP)
        self.validator.validate(filename=filename, content=content)

        clean_original_name = Path(filename.strip()).name

        # Prefijo temporal UTC para trazabilidad y prevención de colisiones
        timestamp = int(datetime.now(timezone.utc).timestamp())
        stored_filename = f"{timestamp}_{clean_original_name}"

        # Persistencia asíncrona no bloqueante mediante la interfaz inyectada
        saved_path = await self.storage_service.save_file(
            filename=stored_filename,
            content=content,
        )

        resolved_content_type = content_type or DEFAULT_CSV_CONTENT_TYPE

        # Construcción de la entidad de dominio para validar invariantes
        uploaded_file = UploadedFile(
            filename=stored_filename,
            original_filename=clean_original_name,
            file_path=saved_path,
            size_bytes=len(content),
            content_type=resolved_content_type,
        )

        return FileUploadDTO(
            filename=uploaded_file.filename,
            original_filename=uploaded_file.original_filename,
            file_path=str(uploaded_file.file_path),
            size_bytes=uploaded_file.size_bytes,
            content_type=uploaded_file.content_type,
        )
