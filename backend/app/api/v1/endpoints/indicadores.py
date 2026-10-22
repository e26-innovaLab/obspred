"""Controlador y endpoints asociados a la consulta de indicadores."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    provide_indicador_repository,
    provide_series_historicas_service,
)
from app.api.v1.schemas.indicadores_schema import (
    IndicadoresFilterSchema,
    IndicadoresResponseSchema,
    IndicadorItemSchema,
)
from app.api.v1.schemas.response_schema import (
    ResponseMeta,
    create_success_response,
)
from app.api.v1.schemas.series_historicas_schema import (
    PuntoSerieItemSchema,
    SerieHistoricaDataSchema,
    SeriesHistoricasFilterSchema,
    SeriesHistoricasResponseSchema,
)
from app.application.dtos.series_historicas_dto import ConsultaSerieHistoricaDTO
from app.application.services.series_historicas_service import (
    SeriesHistoricasService,
)
from app.core.constants import INDICADORES_ROUTE, OPENAPI_TAG_INDICADORES
from app.domain.exceptions.indicador_exceptions import SerieNoEncontradaError
from app.domain.interfaces.indicador_repository import IIndicadorRepository

indicadores_router = APIRouter(
    prefix=INDICADORES_ROUTE,
    tags=[OPENAPI_TAG_INDICADORES],
)


@indicadores_router.get(
    "/series-historicas",
    response_model=SeriesHistoricasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar serie temporal histórica de un indicador",
    description=(
        "Obtiene la serie temporal completa de un indicador ordenado "
        "cronológicamente para análisis y visualización gráfica."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Serie histórica recuperada con éxito.",
            "model": SeriesHistoricasResponseSchema,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ("No se encontraron observaciones para el filtro indicado."),
        },
    },
)
async def get_serie_historica(
    filtros: Annotated[SeriesHistoricasFilterSchema, Query()],
    service: Annotated[
        SeriesHistoricasService,
        Depends(provide_series_historicas_service),
    ],
) -> SeriesHistoricasResponseSchema:
    """Procesa la obtención de series históricas validando invariantes y filtros."""
    consulta = ConsultaSerieHistoricaDTO(
        pais=filtros.pais,
        indicador=filtros.indicador,
        sector=filtros.sector,
        periodo_desde=filtros.desde,
        periodo_hasta=filtros.hasta,
    )
    try:
        resultado = await service.ejecutar(consulta)
    except SerieNoEncontradaError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    data = SerieHistoricaDataSchema(
        pais=resultado.pais,
        indicador=resultado.indicador,
        sector=resultado.sector,
        total_observaciones=resultado.total_observaciones,
        observaciones=[
            PuntoSerieItemSchema(
                periodo=obs.periodo,
                valor=obs.valor,
                tipo=obs.tipo,
                fuente=obs.fuente,
            )
            for obs in resultado.observaciones
        ],
    )
    meta = ResponseMeta(
        total=resultado.total_observaciones,
        extra={"filtros": filtros.model_dump()},
    )

    return create_success_response(
        data=data,
        message="Serie histórica recuperada con éxito.",
        status_code=status.HTTP_200_OK,
        meta=meta,
    )

#INDICADORES 
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
