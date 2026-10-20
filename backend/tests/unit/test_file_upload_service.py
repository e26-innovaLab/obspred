"""Pruebas unitarias para el caso de uso y servicio FileUploadService."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.file_upload_service import FileUploadService
from app.application.validators.csv_file_validator import CsvFileValidator
from app.domain.exceptions.file_upload import (
    EmptyFileException,
    InvalidFileExtensionException,
)
from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator


class FakeStorageService(IFileStorageService):
    """Implementación simulada de IFileStorageService para pruebas unitarias."""

    def __init__(self) -> None:
        self.saved_files: dict[str, bytes] = {}

    async def save_file(self, filename: str, content: bytes) -> Path:
        self.saved_files[filename] = content
        return Path(f"/mock/uploads/{filename}")

    async def file_exists(self, filename: str) -> bool:
        return filename in self.saved_files

    async def delete_file(self, filename: str) -> bool:
        if filename in self.saved_files:
            del self.saved_files[filename]
            return True
        return False


@pytest.mark.asyncio
async def test_upload_csv_success() -> None:
    """Verifica que un archivo CSV válido se procese y almacene correctamente."""
    storage_mock = FakeStorageService()
    validator = CsvFileValidator()
    service = FileUploadService(
        storage_service=storage_mock,
        validator=validator,
    )

    filename = "indicadores_2026.csv"
    content = b"pais,periodo,desempleo\nArgentina,2026-Q1,7.2\n"

    result = await service.upload_csv(
        filename=filename,
        content=content,
        content_type="text/csv",
    )

    assert result.original_filename == filename
    assert result.filename.endswith("_indicadores_2026.csv")
    assert result.size_bytes == len(content)
    assert result.content_type == "text/csv"
    assert "uploads" in result.file_path
    assert result.filename in storage_mock.saved_files


@pytest.mark.asyncio
async def test_upload_csv_delegates_to_validator() -> None:
    """Verifica que FileUploadService invoque al validador inyectado."""
    storage_mock = FakeStorageService()
    validator_mock = MagicMock(spec=IFileValidator)
    validator_mock.validate.side_effect = InvalidFileExtensionException("archivo.xlsx")

    service = FileUploadService(
        storage_service=storage_mock,
        validator=validator_mock,
    )

    with pytest.raises(InvalidFileExtensionException):
        await service.upload_csv(filename="archivo.xlsx", content=b"data")

    validator_mock.validate.assert_called_once_with(
        filename="archivo.xlsx",
        content=b"data",
    )


@pytest.mark.asyncio
async def test_upload_csv_rejects_empty_via_validator() -> None:
    """Verifica que rechace archivos vacíos al utilizar CsvFileValidator."""
    storage_mock = FakeStorageService()
    validator = CsvFileValidator()
    service = FileUploadService(
        storage_service=storage_mock,
        validator=validator,
    )

    with pytest.raises(EmptyFileException):
        await service.upload_csv(filename="archivo.csv", content=b"")


@pytest.mark.asyncio
async def test_upload_csv_delegates_to_storage_and_propagates_error() -> None:
    """Verifica que si el servicio de almacenamiento falla, el error se propague."""
    failing_storage = AsyncMock(spec=IFileStorageService)
    failing_storage.save_file.side_effect = RuntimeError("Storage crash")
    validator = CsvFileValidator()

    service = FileUploadService(
        storage_service=failing_storage,
        validator=validator,
    )

    with pytest.raises(RuntimeError, match="Storage crash"):
        await service.upload_csv(
            filename="datos.csv",
            content=b"a,b\n1,2",
        )
