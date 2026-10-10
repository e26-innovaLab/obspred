"""Endpoint de verificación de estado y salud operativa del backend."""

from fastapi import APIRouter, status

from app.api.v1.schemas.health_schema import (
    HealthDataSchema,
    HealthResponseSchema,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.config import settings
from app.core.constants import DEFAULT_API_VERSION, HEALTH_CHECK_ROUTE, HealthStatus

health_router = APIRouter(tags=["Health"])


@health_router.get(
    HEALTH_CHECK_ROUTE,
    response_model=HealthResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verificación de salud del servicio",
    description=(
        "Retorna el estado operativo, versión y entorno del backend con el "
        "formato estándar ApiResponse."
    ),
)
async def check_health() -> HealthResponseSchema:
    """Verifica la operatividad del backend y responde con el estándar REST.

    Returns:
        HealthResponseSchema: Respuesta estándar ApiResponse envolviendo el
            estado del sistema.
    """
    health_data = HealthDataSchema(
        status=HealthStatus.HEALTHY,
        environment=settings.app_env.value,
        version=DEFAULT_API_VERSION,
    )
    return create_success_response(
        data=health_data,
        message="Servicio funcionando correctamente.",
    )
