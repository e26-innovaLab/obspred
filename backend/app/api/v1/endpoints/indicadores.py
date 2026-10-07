"""Controlador y endpoints asociados a la consulta de indicadores."""

from typing import List, Optional

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.indicadores_schema import (
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


def _clean_filter(value: Optional[str]) -> Optional[str]:
    """Limpia cadenas vacías de filtros transformándolas a None.

    Args:
        value: Valor recibido como parámetro query.

    Returns:
        Optional[str]: Cadena limpia sin espacios en blanco o None.
    """
    if value is not None:
        trimmed = value.strip()
        return trimmed if trimmed else None
    return None


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
    pais: Optional[str] = Query(
        default=None,
        description="Filtro jerárquico por país (ej. ARG, URY, CHL)",
    ),
    sector: Optional[str] = Query(
        default=None,
        description="Filtro por sector productivo o económico",
    ),
    ocupacion: Optional[str] = Query(
        default=None,
        description="Filtro por ocupación de referencia",
    ),
    desde: Optional[str] = Query(
        default=None,
        description="Límite temporal inicial del rango (ej. 2023, 2024-Q1)",
    ),
    hasta: Optional[str] = Query(
        default=None,
        description="Límite temporal final del rango (ej. 2024, 2024-Q4)",
    ),
) -> IndicadoresResponseSchema:
    """Procesa la consulta inicial de indicadores aplicando filtros parametrizados.

    Args:
        pais: País de consulta seleccionado.
        sector: Sector económico analizado.
        ocupacion: Ocupación específica evaluada.
        desde: Período inicial del rango solicitado.
        hasta: Período final del rango solicitado.

    Returns:
        IndicadoresResponseSchema: Envoltorio estándar ApiResponse con la lista
            de indicadores y metadatos con el estado de los filtros.
    """
    clean_filters = {
        "pais": _clean_filter(pais),
        "sector": _clean_filter(sector),
        "ocupacion": _clean_filter(ocupacion),
        "desde": _clean_filter(desde),
        "hasta": _clean_filter(hasta),
    }

    # Por ahora devolvemos el OK con lista vacía en data según requerimiento inicial
    data: List[IndicadorItemSchema] = []
    meta = ResponseMeta(
        total=len(data),
        extra={"filtros": clean_filters},
    )

    return create_success_response(
        data=data,
        message="Consulta de indicadores ejecutada con éxito.",
        status_code=status.HTTP_200_OK,
        meta=meta,
    )
