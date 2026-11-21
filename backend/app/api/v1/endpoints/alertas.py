"""Controlador y endpoint para el reporte de alertas y variaciones."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import Depends, provide_alert_service
from app.api.v1.schemas.alertas_schema import (
    AlertasDataSchema,
    AlertasResponseSchema,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.application.services.alertas_service import AlertaService
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
    alert_service: Annotated[
        AlertaService,
        Depends(provide_alert_service),
    ],
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

    Args:
        tipo: Clasificación de la alerta solicitada.
        indicador: Filtro opcional por slug de indicador.
        pais: Filtro opcional por código ISO 3166-1 alpha-3.
        sector: Filtro opcional por sector estratégico.
        alert_service: Servicio de aplicación para cálculo de alertas.

    Returns:
        AlertasResponseSchema: Envoltorio ApiResponse con la lista de eventos
            de alerta detectados.
    """
    resultado = await alert_service.get_alertas(
        pais=pais,
        indicador=indicador,
        sector=sector,
        tipo=tipo,
    )

    return create_success_response(
        data=AlertasDataSchema(alertas=resultado),
        message="Alertas recuperadas con éxito.",
    )
