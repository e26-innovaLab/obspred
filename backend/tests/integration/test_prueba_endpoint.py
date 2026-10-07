"""Pruebas de integración para el controlador de prueba CRUD con estándar ApiResponse."""

import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.core.constants import PRUEBA_ENDPOINT_BORRAR_ROUTE


@pytest.mark.asyncio
async def test_prueba_crud_operations_with_standard_response(
    async_client: AsyncClient,
) -> None:
    """Verifica que todos los verbos HTTP del endpoint de prueba retornen el estándar ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono.
    """
    base_url = f"{settings.api_v1_prefix}{PRUEBA_ENDPOINT_BORRAR_ROUTE}"

    # 1. GET (Read all)
    get_all_response = await async_client.get(base_url)
    assert get_all_response.status_code == 200
    payload_all = get_all_response.json()
    assert payload_all["success"] is True
    assert payload_all["status_code"] == 200
    assert payload_all["data"]["method"] == "GET"
    assert "timestamp" in payload_all

    # 2. GET (Read one)
    get_one_response = await async_client.get(f"{base_url}/123")
    assert get_one_response.status_code == 200
    payload_one = get_one_response.json()
    assert payload_one["success"] is True
    assert payload_one["status_code"] == 200
    assert payload_one["data"]["method"] == "GET"
    assert payload_one["data"]["item_id"] == "123"

    # 3. POST (Create)
    post_payload = {"name": "Item de prueba", "description": "Probando creación"}
    post_response = await async_client.post(base_url, json=post_payload)
    assert post_response.status_code == 201
    payload_post = post_response.json()
    assert payload_post["success"] is True
    assert payload_post["status_code"] == 201
    assert payload_post["data"]["method"] == "POST"
    assert payload_post["data"]["payload"]["name"] == "Item de prueba"

    # 4. PUT (Update)
    put_payload = {"name": "Item modificado", "description": "Probando actualización"}
    put_response = await async_client.put(f"{base_url}/123", json=put_payload)
    assert put_response.status_code == 200
    payload_put = put_response.json()
    assert payload_put["success"] is True
    assert payload_put["status_code"] == 200
    assert payload_put["data"]["item_id"] == "123"
    assert payload_put["data"]["method"] == "PUT"

    # 5. DELETE (Delete)
    delete_response = await async_client.delete(f"{base_url}/123")
    assert delete_response.status_code == 200
    payload_delete = delete_response.json()
    assert payload_delete["success"] is True
    assert payload_delete["status_code"] == 200
    assert payload_delete["data"]["item_id"] == "123"
    assert payload_delete["data"]["method"] == "DELETE"
