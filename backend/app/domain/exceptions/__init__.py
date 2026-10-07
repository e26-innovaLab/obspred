"""Módulo de excepciones del dominio."""

from app.domain.exceptions.base import DomainException, EntityNotFoundException
from app.domain.exceptions.file_upload import (
    EmptyFileException,
    FileSizeExceededException,
    FileStorageException,
    InvalidFileContentException,
    InvalidFileExtensionException,
)

__all__ = [
    "DomainException",
    "EmptyFileException",
    "EntityNotFoundException",
    "FileSizeExceededException",
    "FileStorageException",
    "InvalidFileContentException",
    "InvalidFileExtensionException",
]
