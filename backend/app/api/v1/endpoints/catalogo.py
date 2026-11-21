"""Controlador y endpoint para el catálogo maestro de filtros y taxonomías."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import provide_catalogo_service
from app.api.v1.schemas.catalogo_schema import (
    CatalogoDataSchema,
    CatalogoResponseSchema,
    IndicadorCatalogoDto,
    OcupacionCatalogoDto,
    PaisCatalogoDto,
    PeriodosRangoDto,
    SectorCatalogoDto,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.application.services.catalogo_service import CatalogoService
from app.core.constants import CATALOGO_ROUTE, OPENAPI_TAG_CATALOGO

catalogo_router = APIRouter(
    prefix=CATALOGO_ROUTE,
    tags=[OPENAPI_TAG_CATALOGO],
)


@catalogo_router.get(
    "",
    response_model=CatalogoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Catálogo de taxonomías y filtros globales",
    description=(
        "Retorna la lista de países, sectores, ocupaciones, indicadores y "
        "períodos disponibles a partir de las tablas maestras y observaciones en BD."
    ),
)
async def get_catalogo(
    catalogo_service: Annotated[
        CatalogoService,
        Depends(provide_catalogo_service),
    ],
) -> CatalogoResponseSchema:
    """Procesa la obtención del catálogo unificado para los filtros del frontend.

    Args:
        catalogo_service: Servicio de aplicación inyectado para consulta de taxonomías.

    Returns:
        CatalogoResponseSchema: Envoltorio ApiResponse con taxonomías completas
            (países, sectores, ocupaciones, indicadores y rango de períodos).
    """
    catalogo_dto = await catalogo_service.get_catalogo()

    data = CatalogoDataSchema(
        paises=[PaisCatalogoDto(id=p.id, nombre=p.nombre) for p in catalogo_dto.paises],
        sectores=[
            SectorCatalogoDto(id=s.id, nombre=s.nombre, isic=s.isic)
            for s in catalogo_dto.sectores
        ],
        ocupaciones=[
            OcupacionCatalogoDto(
                id=o.id,
                nombre=o.nombre,
                sector=o.sector,
                isco=o.isco,
            )
            for o in catalogo_dto.ocupaciones
        ],
        indicadores=[
            IndicadorCatalogoDto(
                id=i.id,
                nombre=i.nombre,
                unidad=i.unidad,
                frecuencias=i.frecuencias,
                desagregaciones=i.desagregaciones,
                descripcion=i.descripcion,
            )
            for i in catalogo_dto.indicadores
        ],
        periodos=PeriodosRangoDto(
            min=catalogo_dto.periodos.min,
            max=catalogo_dto.periodos.max,
        ),
    )

    return create_success_response(
        data=data,
        message="Catálogo de taxonomías recuperado con éxito.",
    )
