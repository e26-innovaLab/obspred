"""Controlador y endpoints asociados a la consulta de indicadores."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import provide_indicador_repository
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
from app.domain.interfaces.indicador_repository import IIndicadorRepository

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
    repository: Annotated[
        IIndicadorRepository,
        Depends(provide_indicador_repository),
    ],
) -> IndicadoresResponseSchema:
    """Procesa la consulta de indicadores aplicando filtros jerárquicos en repositorio.

    Args:
        filtros: Parámetros validados y sanitizados de filtrado jerárquico.
        repository: Repositorio de indicadores inyectado.

    Returns:
        IndicadoresResponseSchema: Envoltorio estándar ApiResponse con la lista
            de indicadores y metadatos con el estado de los filtros.
    """
    db_records = await repository.get_by_filters(
        pais=filtros.pais,
        sector=filtros.sector,
        ocupacion=filtros.ocupacion,
        desde=filtros.desde,
        hasta=filtros.hasta,
    )

    data: list[IndicadorItemSchema] = [
        IndicadorItemSchema(
            pais=r.pais,
            sector=r.sector,
            ocupacion=r.ocupacion,
            indicador=r.indicador,
            periodo=r.periodo,
            valor=r.valor,
            tipo=r.tipo,
            fuente=r.fuente,
            fecha_actualizacion=r.fecha_actualizacion.isoformat(),
        )
        for r in db_records
    ]

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
