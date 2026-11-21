"""Endpoint de verificación de estado y salud del backend y fuentes externas."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import provide_external_services_health_service
from app.api.v1.schemas.health_schema import (
    ExternalServicesHealthDataSchema,
    ExternalServicesHealthResponseSchema,
    ExternalServiceStatusSchema,
    HealthDataSchema,
    HealthResponseSchema,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.application.services.external_services_health_service import (
    ExternalServicesHealthService,
)
from app.core.config import settings
from app.core.constants import (
    DEFAULT_API_VERSION,
    HEALTH_CHECK_ROUTE,
    HEALTH_EXTERNAL_ROUTE,
    HEALTH_SERVICES_ROUTE,
    OPENAPI_TAG_HEALTH,
    HealthStatus,
)

health_router = APIRouter(tags=[OPENAPI_TAG_HEALTH])


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


@health_router.get(
    HEALTH_SERVICES_ROUTE,
    response_model=ExternalServicesHealthResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verificación de salud de servicios y fuentes externas",
    description=(
        "Evalúa de una sola vez y concurrentemente el estado operativo, "
        "disponibilidad y latencia de todos los conectores externos oficiales "
        "(Banco Mundial, SIMEL Chile, Datos Argentina, Banco Central de Chile, "
        "ILOSTAT y ESCO) bajo el formato estándar ApiResponse."
    ),
)
@health_router.get(
    HEALTH_EXTERNAL_ROUTE,
    response_model=ExternalServicesHealthResponseSchema,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def check_external_services_health(
    service: Annotated[
        ExternalServicesHealthService,
        Depends(provide_external_services_health_service),
    ],
) -> ExternalServicesHealthResponseSchema:
    """Evalúa la conectividad de todos los servicios externos en paralelo.

    Args:
        service: Orquestador inyectado de chequeo de conectores externos.

    Returns:
        ExternalServicesHealthResponseSchema: Envoltorio ApiResponse con el estado
            global y el detalle por conector.
    """
    report = await service.check_all_services()
    data = ExternalServicesHealthDataSchema(
        overall_status=report.overall_status,
        total_services=report.total_services,
        healthy_count=report.healthy_count,
        unhealthy_count=report.unhealthy_count,
        services=[
            ExternalServiceStatusSchema(
                source_id=s.source_id,
                name=s.name,
                status=s.status,
                is_available=s.is_available,
                latency_ms=s.latency_ms,
                url=s.url,
                error=s.error,
            )
            for s in report.services
        ],
    )
    return create_success_response(
        data=data,
        message="Diagnóstico de servicios externos completado con éxito.",
        status_code=status.HTTP_200_OK,
    )
