"""Servicio de infraestructura para persistencia de archivos en disco local."""

from pathlib import Path
from typing import Union

import anyio

from app.domain.exceptions.file_upload import FileStorageException
from app.domain.interfaces.file_storage_service import IFileStorageService


class LocalFileStorageService(IFileStorageService):
    """Implementación de almacenamiento físico en el sistema de archivos local.

    Utiliza operaciones en subprocesos delegados (anyio.to_thread) para evitar
    el bloqueo del bucle de eventos asíncrono (Event Loop) de FastAPI.

    Attributes:
        base_dir: Directorio base de persistencia de archivos.
    """

    def __init__(self, base_dir: Union[str, Path]) -> None:
        """Inicializa el servicio configurando el directorio base.

        Args:
            base_dir: Ruta del directorio local donde se guardarán los archivos.
        """
        self.base_dir = Path(base_dir)

    def _sync_write(self, destination: Path, content: bytes) -> None:
        """Operación síncrona interna para escritura de bytes en disco."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    async def save_file(self, filename: str, content: bytes) -> Path:
        """Persiste el archivo de forma segura y no bloqueante en el almacenamiento.

        Crea el directorio si no existe y sanitiza el nombre del archivo para
        prevenir vulnerabilidades de Path Traversal.

        Args:
            filename: Nombre del archivo que se persistirá.
            content: Contenido binario a escribir.

        Returns:
            Path: Ruta del archivo almacenado.

        Raises:
            FileStorageException: Si ocurre un fallo de I/O al escribir en disco.
        """
        clean_filename = Path(filename).name
        destination = self.base_dir / clean_filename
        try:
            await anyio.to_thread.run_sync(self._sync_write, destination, content)
            return destination
        except Exception as exc:
            raise FileStorageException(
                filename=clean_filename,
                reason=f"Fallo de I/O en sistema de archivos: {exc}",
            ) from exc

    async def file_exists(self, filename: str) -> bool:
        """Verifica si un archivo existe en el directorio de almacenamiento.

        Args:
            filename: Nombre del archivo a consultar.

        Returns:
            bool: True si el archivo existe físicamente, False en caso contrario.
        """
        clean_filename = Path(filename).name
        target = self.base_dir / clean_filename
        return await anyio.to_thread.run_sync(target.exists)

    async def delete_file(self, filename: str) -> bool:
        """Elimina de forma segura un archivo existente en disco.

        Args:
            filename: Nombre del archivo a eliminar.

        Returns:
            bool: True si el archivo existía y fue borrado, False en caso contrario.
        """
        clean_filename = Path(filename).name
        target = self.base_dir / clean_filename

        def _sync_delete() -> bool:
            if target.exists() and target.is_file():
                target.unlink()
                return True
            return False

        return await anyio.to_thread.run_sync(_sync_delete)
