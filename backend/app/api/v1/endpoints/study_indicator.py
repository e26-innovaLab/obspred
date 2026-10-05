"""Controlador / Endpoints de ejemplo para estudiar el uso de Services en FastAPI.

Demuestra cómo el controlador actúa exclusivamente como capa de transporte:
1. Valida parámetros de entrada con Pydantic.
2. Recibe el servicio inyectado vía `StudyIndicatorServiceDep`.
3. Delega la lógica de negocio al servicio.
4. Devuelve la respuesta estandarizada `ApiResponse[T]`.
"""

from typing import Optional

from fastapi import APIRouter, Path, Query, status

from app.api.dependencies import StudyIndicatorServiceDep
from app.api.v1.schemas.response_schema import create_success_response
from app.api.v1.schemas.study_indicator_schema import (
    CreateStudyIndicatorPayload,
    StudyIndicatorApiResponse,
    StudyIndicatorListApiResponse,
    StudyIndicatorResponseData,
)
from app.application.dtos.study_indicator_dto import (
    CreateStudyIndicatorDTO,
    StudyIndicatorFilterDTO,
)
from app.core.constants import STUDY_INDICATORS_ROUTE

study_indicator_router = APIRouter(
    prefix=STUDY_INDICATORS_ROUTE,
    tags=["Study - Services Pattern"],
)


@study_indicator_router.get(
    "",
    response_model=StudyIndicatorListApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar indicadores de estudio",
    description="Demuestra cómo el endpoint delega el filtrado al servicio.",
)
async def list_indicators(
    service: StudyIndicatorServiceDep,
    country: Optional[str] = Query(
        None,
        description="Filtrar por país (AR, CL, UY)",
        min_length=2,
        max_length=2,
    ),
    sector: Optional[str] = Query(
        None,
        description="Filtrar por sector (Tecnología, Salud, etc.)",
    ),
) -> StudyIndicatorListApiResponse:
    """Consulta indicadores delegando al servicio inyectado."""
    dto_filters = StudyIndicatorFilterDTO(country=country, sector=sector)
    domain_indicators = await service.list_indicators(filters=dto_filters)

    # Conversión de entidades de dominio a esquema Pydantic de salida
    data = [
        StudyIndicatorResponseData(
            id=item.id,
            name=item.name,
            country=item.country,
            sector=item.sector,
            value=item.value,
            unit=item.unit,
            source=item.source,
            updated_at=item.updated_at,
        )
        for item in domain_indicators
    ]

    return create_success_response(
        data=data,
        message="Listado de indicadores obtenido correctamente mediante el servicio.",
    )


@study_indicator_router.get(
    "/{indicator_id}",
    response_model=StudyIndicatorApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener indicador por ID",
    description=(
        "Si el ID no existe, el servicio lanza EntityNotFoundException, la cual "
        "es capturada globalmente devolviendo HTTP 404 en formato ApiResponse."
    ),
)
async def get_indicator(
    service: StudyIndicatorServiceDep,
    indicator_id: str = Path(..., description="ID del indicador a consultar"),
) -> StudyIndicatorApiResponse:
    """Busca un indicador por ID a través del servicio inyectado."""
    indicator = await service.get_indicator_by_id(indicator_id=indicator_id)

    data = StudyIndicatorResponseData(
        id=indicator.id,
        name=indicator.name,
        country=indicator.country,
        sector=indicator.sector,
        value=indicator.value,
        unit=indicator.unit,
        source=indicator.source,
        updated_at=indicator.updated_at,
    )

    return create_success_response(
        data=data,
        message=f"Indicador '{indicator_id}' recuperado con éxito.",
    )


@study_indicator_router.post(
    "",
    response_model=StudyIndicatorApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo indicador",
    description=(
        "Si se envía un país no permitido o un valor negativo, el servicio lanza "
        "DomainException, devolviendo HTTP 400 de forma automática."
    ),
)
async def create_indicator(
    payload: CreateStudyIndicatorPayload,
    service: StudyIndicatorServiceDep,
) -> StudyIndicatorApiResponse:
    """Registra un nuevo indicador validando reglas de negocio en el servicio."""
    dto = CreateStudyIndicatorDTO(
        name=payload.name,
        country=payload.country,
        sector=payload.sector,
        value=payload.value,
        unit=payload.unit,
        source=payload.source,
    )

    created_indicator = await service.create_indicator(dto=dto)

    data = StudyIndicatorResponseData(
        id=created_indicator.id,
        name=created_indicator.name,
        country=created_indicator.country,
        sector=created_indicator.sector,
        value=created_indicator.value,
        unit=created_indicator.unit,
        source=created_indicator.source,
        updated_at=created_indicator.updated_at,
    )

    return create_success_response(
        data=data,
        message="Indicador creado exitosamente a través del servicio.",
        status_code=status.HTTP_201_CREATED,
    )
