"""Módulo de excepciones del dominio."""

from app.domain.exceptions.base import DomainException, EntityNotFoundException
from app.domain.exceptions.file_upload import (
    EmptyFileException,
    FileSizeExceededException,
    FileStorageException,
    InvalidFileContentException,
    InvalidFileExtensionException,
)
from app.domain.exceptions.indice_empleabilidad import (
    InsufficientDataException,
    InvalidOccupationException,
)
from app.domain.exceptions.simel_exceptions import (
    InvalidSimelCsvException,
    SimelWafBlockedException,
)

__all__ = [
    "DomainException",
    "EmptyFileException",
    "EntityNotFoundException",
    "FileSizeExceededException",
    "FileStorageException",
    "InsufficientDataException",
    "InvalidFileContentException",
    "InvalidFileExtensionException",
    "InvalidOccupationException",
    "InvalidSimelCsvException",
    "SimelWafBlockedException",
]
