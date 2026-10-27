"""Pruebas unitarias para el validador CsvFileValidator."""

import pytest

from app.application.validators.csv_file_validator import CsvFileValidator
from app.domain.exceptions.file_upload import (
    EmptyFileException,
    FileSizeExceededException,
    InvalidFileContentException,
    InvalidFileExtensionException,
)


def test_validator_accepts_valid_csv() -> None:
    """Verifica que un archivo CSV válido pase la validación sin excepciones."""
    validator = CsvFileValidator(max_size_bytes=1024)
    # No debe levantar ninguna excepción
    validator.validate(
        filename="indicadores.csv",
        content=b"pais,sector\nArgentina,Tecnologia\n",
    )


def test_validator_accepts_uppercase_csv_extension() -> None:
    """Verifica que acepte extensiones en mayúscula como .CSV."""
    validator = CsvFileValidator()
    validator.validate(filename="DATA.CSV", content=b"a,b\n1,2\n")


@pytest.mark.parametrize(
    "invalid_filename",
    [
        "reporte.xlsx",
        "datos.json",
        "archivo.pdf",
        "sin_extension",
        "",
        "   ",
    ],
)
def test_validator_rejects_invalid_extension(invalid_filename: str) -> None:
    """Verifica el rechazo de extensiones no permitidas."""
    validator = CsvFileValidator()
    with pytest.raises(InvalidFileExtensionException):
        validator.validate(filename=invalid_filename, content=b"a,b\n1,2")


@pytest.mark.parametrize(
    "empty_content",
    [
        b"",
        b"   ",
        b"\n\t  \r\n",
    ],
)
def test_validator_rejects_empty_content(empty_content: bytes) -> None:
    """Verifica el rechazo de archivos vacíos o con solo espacios."""
    validator = CsvFileValidator()
    with pytest.raises(EmptyFileException):
        validator.validate(filename="datos.csv", content=empty_content)


def test_validator_rejects_file_exceeding_max_size() -> None:
    """Verifica el rechazo de archivos que superan el límite en bytes."""
    validator = CsvFileValidator(max_size_bytes=50)
    large_content = b"a" * 51

    with pytest.raises(FileSizeExceededException) as exc_info:
        validator.validate(filename="grande.csv", content=large_content)

    assert exc_info.value.size_bytes == 51
    assert exc_info.value.max_bytes == 50


def test_validator_rejects_binary_file_with_null_bytes() -> None:
    """Verifica el rechazo de archivos binarios disfrazados de CSV."""
    validator = CsvFileValidator()
    binary_content = b"MZ\x00\x00\x03\x00\x00\x00executable_header"

    with pytest.raises(InvalidFileContentException) as exc_info:
        validator.validate(filename="falso.csv", content=binary_content)

    assert "secuencias binarias" in exc_info.value.detail
