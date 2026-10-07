"""Contrato de interfaz (puerto) para almacenamiento de archivos."""

from abc import ABC, abstractmethod
from pathlib import Path


class IFileStorageService(ABC):
    """Interfaz abstracta que define las operaciones de persistencia de archivos.

    Permite desacoplar la lógica de aplicación del medio físico o proveedor
    de almacenamiento concreto (almacenamiento local, S3, Azure Blob, etc.).
    """

    @abstractmethod
    async def save_file(self, filename: str, content: bytes) -> Path:
        """Persiste el contenido de un archivo en el medio configurado.

        Args:
            filename: Nombre con el que se almacenará el archivo en el destino.
            content: Contenido binario del archivo.

        Returns:
            Path: Ruta del archivo persistido en el sistema de almacenamiento.

        Raises:
            FileStorageException: Si ocurre un error durante el guardado físico.
        """
        pass

    @abstractmethod
    async def file_exists(self, filename: str) -> bool:
        """Verifica si un archivo con el nombre especificado existe en almacenamiento.

        Args:
            filename: Nombre del archivo a consultar.

        Returns:
            bool: True si el archivo existe físicamente, False en caso contrario.
        """
        pass

    @abstractmethod
    async def delete_file(self, filename: str) -> bool:
        """Elimina un archivo existente del sistema de almacenamiento.

        Args:
            filename: Nombre del archivo a eliminar.

        Returns:
            bool: True si el archivo fue eliminado, False si no existía.
        """
        pass
