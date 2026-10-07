"""Controlador y endpoints asociados a la consulta de indicadores."""

from typing import Annotated, List

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.indicadores_schema import (
    IndicadoresFilterSchema,
    IndicadoresResponseSchema,
    IndicadorItemSchema,
)
from app.api.v1.schemas.response_schema import (
    ResponseMeta,
    create_success_response,
)
from app.core.constants import INDICADORES_ROUTE

indicadores_router = APIRouter(
    prefix=INDICADORES_ROUTE,
    tags=["Indicadores"],
)


@indicadores_router.get(
    "",
    response_model=IndicadoresResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar indicadores socioeconómicos, laborales y educativos",
    description=(
        "Obtiene indicadores normalizados bajo filtros jerárquicos: "
        "país, sector, ocupación y rango temporal (desde / hasta)."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Consulta de indicadores procesada con éxito.",
            "model": IndicadoresResponseSchema,
        },
    },
)
async def get_indicadores(
    filtros: Annotated[IndicadoresFilterSchema, Query()],
) -> IndicadoresResponseSchema:
    """Procesa la consulta inicial de indicadores aplicando filtros parametrizados.

    Args:
        filtros: Parámetros validados y sanitizados de filtrado jerárquico.

    Returns:
        IndicadoresResponseSchema: Envoltorio estándar ApiResponse con la lista
            de indicadores y metadatos con el estado de los filtros.
    """
    # Por ahora devolvemos el OK con lista vacía en data según requerimiento inicial
    data: List[IndicadorItemSchema] = []
    meta = ResponseMeta(
        total=len(data),
        extra={"filtros": filtros.model_dump()},
    )

    return create_success_response(
        data=data,
        message="Consulta de indicadores ejecutada con éxito.",
        status_code=status.HTTP_200_OK,
        meta=meta,
    )
