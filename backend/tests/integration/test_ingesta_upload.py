"""Pruebas de integración para el endpoint POST /api/v1/ingesta/upload."""

import shutil
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import (
    API_V1_PREFIX,
    INGESTA_ROUTE,
    INGESTA_UPLOAD_ROUTE,
)


@pytest.fixture(autouse=True)
def cleanup_test_uploads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Configura un directorio temporal aislado para cada prueba y lo limpia.

    Args:
        tmp_path: Directorio temporal de Pytest.
        monkeypatch: Modificador dinámico de configuración.
    """
    test_upload_dir = tmp_path / "test_uploads"
    monkeypatch.setattr(settings, "upload_dir", str(test_upload_dir))
    yield
    if test_upload_dir.exists():
        shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_upload_valid_csv_returns_201_and_persists_file(
    async_client: AsyncClient,
) -> None:
    """Verifica carga exitosa de CSV con código 201 y formato ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas de integración.
    """
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"
    csv_content = b"pais,sector,periodo,desempleo\nArgentina,Tecnologia,2026-Q1,5.4\n"
    files = {
        "file": ("indicadores.csv", csv_content, "text/csv"),
    }

    response = await async_client.post(url, files=files)

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 201
    assert payload["message"] == "Archivo CSV subido y persistido con éxito."
    assert payload["data"] is not None
    assert payload["data"]["original_filename"] == "indicadores.csv"
    assert payload["data"]["filename"].endswith("_indicadores.csv")
    assert payload["data"]["size_bytes"] == len(csv_content)
    assert payload["data"]["content_type"] == "text/csv"

    # Verificar existencia física del archivo persistido
    persisted_path = Path(payload["data"]["file_path"])
    assert persisted_path.exists()
    assert persisted_path.read_bytes() == csv_content


@pytest.mark.asyncio
async def test_upload_non_csv_file_returns_400_domain_violation(
    async_client: AsyncClient,
) -> None:
    """Verifica que archivo no CSV retorne 400 y código DOMAIN_RULE_VIOLATION.

    Args:
        async_client: Cliente HTTP asíncrono.
    """
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"
    files = {
        "file": (
            "reporte.xlsx",
            b"contenido_binario_excel",
            "application/vnd.ms-excel",
        ),
    }

    response = await async_client.post(url, files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert "Solo se admiten archivos con extensión '.csv'" in payload["message"]
    assert payload["errors"] is not None
    assert payload["errors"][0]["code"] == "DOMAIN_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_upload_empty_csv_file_returns_400(
    async_client: AsyncClient,
) -> None:
    """Verifica que un archivo CSV vacío de 0 bytes retorne código 400.

    Args:
        async_client: Cliente HTTP asíncrono.
    """
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"
    files = {
        "file": ("vacio.csv", b"", "text/csv"),
    }

    response = await async_client.post(url, files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert "está vacío" in payload["message"]
    assert payload["errors"][0]["code"] == "DOMAIN_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_upload_binary_masked_as_csv_returns_400(
    async_client: AsyncClient,
) -> None:
    """Verifica que un archivo binario disfrazado como .csv sea rechazado con 400.

    Args:
        async_client: Cliente HTTP asíncrono.
    """
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"
    files = {
        "file": ("malware.csv", b"MZ\x00\x00\x00fake_binary", "text/csv"),
    }

    response = await async_client.post(url, files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert "secuencias binarias" in payload["message"]


@pytest.mark.asyncio
async def test_upload_file_exceeding_max_size_returns_400(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que un archivo que excede el límite configurado sea rechazado.

    Args:
        async_client: Cliente HTTP asíncrono.
        monkeypatch: Modificador dinámico de configuración.
    """
    monkeypatch.setattr(settings, "max_upload_size_bytes", 100)
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"
    files = {
        "file": ("pesado.csv", b"col1,col2\n" + b"1,2\n" * 50, "text/csv"),
    }

    response = await async_client.post(url, files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert "excede el tamaño máximo" in payload["message"]


@pytest.mark.asyncio
async def test_upload_missing_file_payload_returns_422(
    async_client: AsyncClient,
) -> None:
    """Verifica que petición multipart sin 'file' retorne 422 de validación.

    Args:
        async_client: Cliente HTTP asíncrono.
    """
    url = f"{API_V1_PREFIX}{INGESTA_ROUTE}{INGESTA_UPLOAD_ROUTE}"

    response = await async_client.post(url, data={"otro_campo": "valor"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 422
    assert payload["errors"][0]["code"] == "VALIDATION_ERROR"
