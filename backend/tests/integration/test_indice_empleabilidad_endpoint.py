from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.api.dependencies import provide_indice_empleabilidad_repository
from app.core.config import settings
from app.core.constants import INDICE_EMPLEABILIDAD_ROUTE
from app.infrastructure.persistence.repositories import (
    SqlAlchemyIndiceEmpleabilidadRepository,
)
from app.main import app


@pytest.fixture(autouse=True)
def override_repository_dependency() -> Generator[None, None, None]:
    """Aísla el repositorio para pruebas de integración evitando timeouts de red."""
    app.dependency_overrides[provide_indice_empleabilidad_repository] = lambda: (
        SqlAlchemyIndiceEmpleabilidadRepository(session=None)
    )
    yield
    app.dependency_overrides.pop(provide_indice_empleabilidad_repository, None)


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_por_id_exitoso(
    async_client: AsyncClient,
) -> None:
    """Verifica consulta exitosa por ID normalizado con envoltorio ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/dev-software"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["errors"] is None
    assert "timestamp" in payload

    data = payload["data"]
    assert data["ocupacion_id"] == "dev-software"
    assert data["ocupacion_nombre"] == "Desarrollador/a de software"
    assert 0.0 <= data["score"] <= 100.0
    assert data["nivel"] in ["Muy Alto", "Alto", "Medio", "Bajo"]
    assert data["tipo"] == "calculado"
    assert "fuente" in data and len(data["fuente"]) > 0
    assert "fecha_actualizacion" in data
    assert "metodologia" in data

    # Verificación de las 4 dimensiones metodológicas
    dimensiones = data["dimensiones"]
    assert len(dimensiones) == 4
    nombres_dim = {d["nombre"] for d in dimensiones}
    assert "Demanda de puestos" in nombres_dim
    assert "Estabilidad salarial" in nombres_dim
    assert "Cobertura formativa" in nombres_dim
    assert "Crecimiento reciente" in nombres_dim

    suma_pesos = sum(d["peso"] for d in dimensiones)
    assert round(suma_pesos, 2) == 1.00

    # Verificación de serie histórica de evolución (≥ 3 períodos según Principio 5)
    evolucion = data["evolucion"]
    assert len(evolucion) >= 3

    # Metadatos
    assert payload["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_por_nombre(
    async_client: AsyncClient,
) -> None:
    """Verifica que resolver por nombre o slug alternativo funcione adecuadamente.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = (
        f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}"
        "/Desarrollador%20de%20software"
    )
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["ocupacion_id"] == "dev-software"


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_con_filtros(
    async_client: AsyncClient,
) -> None:
    """Verifica que los filtros territoriales y temporales se apliquen y reporten.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/enfermeria"
    params = {
        "pais": "CHL",
        "sector": "salud",
        "periodo": "2026-Q1",
    }
    response = await async_client.get(url, params=params)

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]

    assert data["pais"] == "CHL"
    assert data["sector"] == "salud"
    assert data["periodo"] == "2026-Q1"
    assert "Chile" in data["fuente"] or "SENCE" in data["fuente"]

    meta_filtros = payload["meta"]["extra"]["filtros"]
    assert meta_filtros["pais"] == "CHL"
    assert meta_filtros["sector"] == "salud"
    assert meta_filtros["periodo"] == "2026-Q1"


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_filtros_vacios(
    async_client: AsyncClient,
) -> None:
    """Verifica que filtros con cadenas vacías o espacios sean sanitizados a None.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/analista-datos"
    params = {
        "pais": "   ",
        "sector": "",
        "periodo": "  ",
    }
    response = await async_client.get(url, params=params)

    assert response.status_code == 200
    payload = response.json()
    meta_filtros = payload["meta"]["extra"]["filtros"]
    assert meta_filtros["pais"] is None
    assert meta_filtros["sector"] is None
    assert meta_filtros["periodo"] is None


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_ocupacion_no_encontrada(
    async_client: AsyncClient,
) -> None:
    """Verifica que una ocupación inexistente retorne HTTP 404 bajo ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = (
        f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}"
        "/ocupacion-inexistente-xyz-999"
    )
    response = await async_client.get(url)

    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 404
    assert payload["data"] is None
    assert len(payload["errors"]) == 1
    assert payload["errors"][0]["code"] == "ENTITY_NOT_FOUND"
    assert payload["errors"][0]["field"] == "Occupation"


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_ocupacion_espacios_en_blanco(
    async_client: AsyncClient,
) -> None:
    """Verifica que una ocupación compuesta solo por espacios retorne HTTP 400.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/%20%20%20"
    response = await async_client.get(url)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert payload["data"] is None
    assert len(payload["errors"]) == 1
    assert payload["errors"][0]["code"] == "DOMAIN_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_get_indice_empleabilidad_trazabilidad_total(
    async_client: AsyncClient,
) -> None:
    """Verifica el cumplimiento estricto del Principio 3 (Trazabilidad Total).

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = (
        f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}"
        "/tecnico-energias-renovables"
    )
    response = await async_client.get(url, params={"pais": "ARG"})

    assert response.status_code == 200
    data = response.json()["data"]

    # Debe poseer fuente, fecha de actualización y tipo explícito
    assert data["tipo"] == "calculado"
    assert data["fuente"] != ""
    assert data["fecha_actualizacion"] == "2026-09-30"
    assert "Metodología v1" in data["metodologia"]


@pytest.mark.asyncio
async def test_get_ranking_ocupaciones_default_catalogo(
    async_client: AsyncClient,
) -> None:
    """Verifica consulta de ranking por defecto desde catálogo con sesión nula.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/ranking"
    response = await async_client.get(url, params={"pais": "ARG,CHL"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["errors"] is None

    ocupaciones = payload["data"]["ocupaciones"]
    assert len(ocupaciones) > 0

    # Principio 4: Con sesión nula en pruebas no hay avisos en BD -> None honesto
    for item in ocupaciones:
        assert "ocupacion_id" in item
        assert "nombre" in item
        assert "indice_empleabilidad" in item
        assert 0.0 <= item["indice_empleabilidad"] <= 100.0
        assert item["pais"] in ["ARG", "CHL"]
        assert "fuente" in item and len(item["fuente"]) > 0
        assert item["puestos_disponibles"] is None

    # Ordenamiento por score descendente
    scores = [item["indice_empleabilidad"] for item in ocupaciones]
    assert scores == sorted(scores, reverse=True)

    # Metadatos
    assert payload["meta"]["total"] == len(ocupaciones)


@pytest.mark.asyncio
async def test_get_ranking_ocupaciones_orden_puestos(
    async_client: AsyncClient,
) -> None:
    """Verifica que el parámetro de orden 'puestos' sea procesado correctamente.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/ranking"
    response = await async_client.get(url, params={"pais": "ARG", "orden": "puestos"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["ocupaciones"]) > 0


@pytest.mark.asyncio
async def test_get_ranking_ocupaciones_pais_invalido(
    async_client: AsyncClient,
) -> None:
    """Verifica que un país desconocido retorne HTTP 400 bajo DomainException.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/ranking"
    response = await async_client.get(url, params={"pais": "PAIS_INVENTADO_XYZ"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["status_code"] == 400
    assert payload["errors"][0]["code"] == "DOMAIN_RULE_VIOLATION"


@pytest.mark.asyncio
async def test_get_ranking_ocupaciones_filtro_sector(
    async_client: AsyncClient,
) -> None:
    """Verifica filtrado de ocupaciones por sector estratégico.

    Args:
        async_client: Cliente HTTP asíncrono para pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/ranking"
    response = await async_client.get(
        url, params={"pais": "ARG", "sector": "tecnologia"}
    )

    assert response.status_code == 200
    ocupaciones = response.json()["data"]["ocupaciones"]
    assert len(ocupaciones) > 0
    # Todas las ocupaciones deben pertenecer al sector tecnología del catálogo
    slugs = {item["ocupacion_id"] for item in ocupaciones}
    assert slugs.issubset(
        {
            "dev-software",
            "analista-datos",
            "diseno-ux",
            "soporte-ti",
        }
    )
