"""Pruebas unitarias para el servicio de almacenamiento LocalFileStorageService."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.domain.exceptions.file_upload import FileStorageException
from app.infrastructure.storage.local_file_storage_service import (
    LocalFileStorageService,
)


@pytest.mark.asyncio
async def test_save_file_successfully(tmp_path: Path) -> None:
    """Verifica que el archivo se guarde correctamente en el directorio destino.

    Args:
        tmp_path: Fixture de Pytest que proporciona un directorio temporal.
    """
    storage = LocalFileStorageService(base_dir=tmp_path)
    filename = "test_indicadores.csv"
    content = b"pais,sector,valor\nArgentina,Tecnologia,100\n"

    result_path = await storage.save_file(filename=filename, content=content)

    assert result_path.exists()
    assert result_path.is_file()
    assert result_path.read_bytes() == content
    assert result_path.name == filename


@pytest.mark.asyncio
async def test_save_file_creates_nested_directories_if_not_exist(
    tmp_path: Path,
) -> None:
    """Verifica que cree directorios anidados si no existen previamente.

    Args:
        tmp_path: Directorio temporal de prueba.
    """
    nested_dir = tmp_path / "subcarpeta" / "uploads"
    storage = LocalFileStorageService(base_dir=nested_dir)
    filename = "datos.csv"
    content = b"col1,col2\n1,2\n"

    result_path = await storage.save_file(filename=filename, content=content)

    assert nested_dir.exists()
    assert result_path.exists()
    assert result_path.read_bytes() == content


@pytest.mark.asyncio
async def test_save_file_sanitizes_filename_preventing_path_traversal(
    tmp_path: Path,
) -> None:
    """Verifica que sanitice el nombre evitando ataques de Directory Traversal.

    Args:
        tmp_path: Directorio temporal de prueba.
    """
    storage_dir = tmp_path / "uploads"
    storage = LocalFileStorageService(base_dir=storage_dir)
    malicious_filename = "../../../escape_dir.csv"
    content = b"seguridad,test\n"

    result_path = await storage.save_file(
        filename=malicious_filename,
        content=content,
    )

    # Debe guardarse dentro de storage_dir con solo el nombre base
    assert result_path.parent == storage_dir
    assert result_path.name == "escape_dir.csv"
    assert result_path.exists()


@pytest.mark.asyncio
async def test_file_exists_and_delete_file(tmp_path: Path) -> None:
    """Verifica la consulta de existencia y borrado seguro de archivos.

    Args:
        tmp_path: Directorio temporal de prueba.
    """
    storage = LocalFileStorageService(base_dir=tmp_path)
    filename = "existente.csv"

    # Inicialmente no existe
    assert await storage.file_exists(filename) is False
    assert await storage.delete_file(filename) is False

    # Guardar archivo
    await storage.save_file(filename, b"a,b\n1,2")
    assert await storage.file_exists(filename) is True

    # Borrar archivo
    deleted = await storage.delete_file(filename)
    assert deleted is True
    assert await storage.file_exists(filename) is False


@pytest.mark.asyncio
async def test_save_file_raises_storage_exception_on_write_error(
    tmp_path: Path,
) -> None:
    """Verifica que capture fallos de I/O y lance FileStorageException.

    Args:
        tmp_path: Directorio temporal de prueba.
    """
    storage = LocalFileStorageService(base_dir=tmp_path)

    with patch.object(
        storage,
        "_sync_write",
        side_effect=OSError("Fallo simulado de disco lleno o sin permisos"),
    ):
        with pytest.raises(FileStorageException) as exc_info:
            await storage.save_file("error.csv", b"data")

    assert "Fallo de I/O en sistema de archivos" in exc_info.value.message
