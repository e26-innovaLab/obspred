"""Pruebas de integración para endpoints de brechas de habilidades."""

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import BRECHAS_ROUTE


@pytest.mark.asyncio
async def test_get_brechas_por_ocupacion_existente(async_client: AsyncClient) -> None:
    """Verifica que la consulta retorne 200 con la envoltura estándar y habilidades."""
    url = f"{settings.api_v1_prefix}{BRECHAS_ROUTE}/desarrollador_software"
    response = await async_client.get(
        url, params={"pais": "ARG", "sector": "Tecnología"}
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"] is not None

    data = payload["data"]
    assert data["pais"] == "ARG"
    assert data["sector"] == "Tecnología"
    assert data["ocupacion"] == "desarrollador_software"
    assert len(data["habilidades"]) > 0

    primera = data["habilidades"][0]
    assert "habilidad" in primera
    assert "demanda" in primera
    assert "ofertaFormativa" in primera
    assert "emergente" in primera
    assert "brecha" in primera
    # Regla de negocio de la brecha: max(0, demanda - oferta)
    assert primera["brecha"] == max(
        0.0, primera["demanda"] - primera["ofertaFormativa"]
    )


@pytest.mark.asyncio
async def test_post_and_get_brechas_persistencia(async_client: AsyncClient) -> None:
    """Verifica la persistencia mediante POST y su posterior
    recuperación mediante GET.
    """
    base_url = f"{settings.api_v1_prefix}{BRECHAS_ROUTE}/arquitecto_cloud"

    post_payload = {
        "habilidades": [
            {
                "habilidad": "Kubernetes",
                "demanda": 92.0,
                "ofertaFormativa": 35.0,
                "emergente": True,
            },
            {
                "habilidad": "Terraform",
                "demanda": 88.0,
                "ofertaFormativa": 40.0,
                "emergente": False,
            },
        ],
        "pais": "CHL",
        "sector": "Tecnología",
    }

    # 1. POST para persistir
    post_res = await async_client.post(base_url, json=post_payload)
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["success"] is True
    assert len(post_data["data"]["habilidades"]) == 2

    k8s = next(
        h for h in post_data["data"]["habilidades"] if h["habilidad"] == "Kubernetes"
    )
    assert k8s["demanda"] == 92.0
    assert k8s["ofertaFormativa"] == 35.0
    assert k8s["emergente"] is True
    assert k8s["brecha"] == 57.0

    # 2. GET para validar que se persiguió en la base de datos
    get_res = await async_client.get(base_url, params={"pais": "CHL"})
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data["data"]["habilidades"]) == 2
    assert any(h["habilidad"] == "Terraform" for h in get_data["data"]["habilidades"])


@pytest.mark.asyncio
async def test_get_brechas_ocupacion_inexistente(async_client: AsyncClient) -> None:
    """Verifica que una ocupación no existente retorne HTTP 404."""
    url = f"{settings.api_v1_prefix}{BRECHAS_ROUTE}/ocupacion_inexistente_12345"
    response = await async_client.get(url)

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert "No se encontraron datos de brecha" in payload["message"]
