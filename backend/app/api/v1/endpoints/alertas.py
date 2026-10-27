"""Controlador y endpoint para el reporte de alertas y variaciones."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.alertas_schema import (
    AlertaItemDto,
    AlertasDataSchema,
    AlertasResponseSchema,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.constants import ALERTAS_ROUTE, OPENAPI_TAG_ALERTAS

alertas_router = APIRouter(
    prefix=ALERTAS_ROUTE,
    tags=[OPENAPI_TAG_ALERTAS],
)


@alertas_router.get(
    "",
    response_model=AlertasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Listado de alertas y cambios significativos",
    description="Retorna alertas activas o puntos de corte para marcadores.",
)
async def get_alertas(
    tipo: Annotated[
        str | None,
        Query(
            description="Tipo de alerta ('variacion_significativa', etc.)",
            examples=["variacion_significativa"],
        ),
    ] = None,
    indicador: Annotated[str | None, Query(description="Filtrar por indicador")] = None,
    pais: Annotated[
        str | None, Query(description="Filtrar por país ISO-3 (ej. 'ARG')")
    ] = None,
    sector: Annotated[str | None, Query(description="Filtrar por sector")] = None,
) -> AlertasResponseSchema:
    """Procesa la consulta de alertas estadísticas.

    # TODO (Backend):
    # 1. Inyectar servicio de alertas o cálculo de variaciones interperíodo.
    # 2. Aplicar umbrales fijados (ej. >5% variación = medio, >8% = alto).
    # 3. Filtrar por tipo de alerta solicitado y país.
    """
    alertas_mock = [
        AlertaItemDto(
            id="puestos_demandados-ARG-2023-Q4",
            pais="ARG",
            indicador="puestos_demandados",
            periodo="2023-Q4",
            variacion_pct=8.0,
            nivel="alto",
            titulo="Puestos demandados: suba de 8 %",
            descripcion="Variación acelerada respecto del período anterior (T3 2023).",
        ),
        AlertaItemDto(
            id="puestos_demandados-ARG-2026-Q2",
            pais="ARG",
            indicador="puestos_demandados",
            periodo="2026-Q2",
            variacion_pct=6.2,
            nivel="medio",
            titulo="Puestos demandados: suba de 6,2 %",
            descripcion="Incremento sostenido impulsado por el sector tecnológico.",
        ),
        AlertaItemDto(
            id="tasa_desempleo-CHL-2025-Q3",
            pais="CHL",
            indicador="tasa_desempleo",
            periodo="2025-Q3",
            variacion_pct=-5.4,
            nivel="medio",
            titulo="Desempleo: reducción del 5,4 %",
            descripcion="Caída positiva de la desocupación en el tercer trimestre.",
        ),
    ]

    resultado = alertas_mock
    if indicador:
        resultado = [a for a in resultado if a.indicador == indicador]
    if pais:
        pais_norm = pais.strip().upper()
        resultado = [a for a in resultado if a.pais == pais_norm]

    return create_success_response(
        data=AlertasDataSchema(alertas=resultado),
        message="Alertas recuperadas con éxito.",
    )
