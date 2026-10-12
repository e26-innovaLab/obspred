"""Controlador y endpoints asociados al Índice de Empleabilidad por ocupación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies import provide_indice_empleabilidad_service
from app.api.v1.schemas.indice_empleabilidad_schema import (
    DimensionIndiceSchema,
    EvolucionIndicePuntoSchema,
    IndiceEmpleabilidadDataSchema,
    IndiceEmpleabilidadFilterSchema,
    IndiceEmpleabilidadResponseSchema,
)
from app.api.v1.schemas.response_schema import (
    ApiResponse,
    ResponseMeta,
    create_success_response,
)
from app.application.services.indice_empleabilidad_service import (
    IndiceEmpleabilidadService,
)
from app.core.constants import INDICE_EMPLEABILIDAD_ROUTE

indice_empleabilidad_router = APIRouter(
    prefix=INDICE_EMPLEABILIDAD_ROUTE,
    tags=["Indice de Empleabilidad"],
)


@indice_empleabilidad_router.get(
    "/{ocupacion}",
    response_model=IndiceEmpleabilidadResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar Índice de Empleabilidad por ocupación",
    description=(
        "Obtiene el Índice de Empleabilidad multidimensional (score 0–100) "
        "para una ocupación específica, incluyendo el desglose de sus 4 "
        "dimensiones ponderadas, nivel cualitativo, trazabilidad total "
        "(fuente oficial, fecha de corte, tipo calculado) y serie histórica."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Índice de Empleabilidad obtenido con éxito.",
            "model": IndiceEmpleabilidadResponseSchema,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Parámetro de ocupación inválido o vacío.",
            "model": ApiResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "La ocupación solicitada no fue encontrada en el sistema.",
            "model": ApiResponse,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Error de validación sintáctica de parámetros.",
            "model": ApiResponse,
        },
    },
)
async def get_indice_empleabilidad_por_ocupacion(
    ocupacion: Annotated[
        str,
        Path(
            description=(
                "Identificador, slug o denominación de la ocupación (ej. dev-software)"
            ),
            min_length=1,
        ),
    ],
    filtros: Annotated[IndiceEmpleabilidadFilterSchema, Query()],
    service: Annotated[
        IndiceEmpleabilidadService,
        Depends(provide_indice_empleabilidad_service),
    ],
) -> IndiceEmpleabilidadResponseSchema:
    """Procesa la consulta del Índice de Empleabilidad para una ocupación.

    Args:
        ocupacion: Identificador o denominación de la ocupación requerida.
        filtros: Parámetros opcionales de filtrado (país, sector, período).
        service: Servicio de aplicación inyectado por FastAPI.

    Returns:
        IndiceEmpleabilidadResponseSchema: Envoltorio estándar ApiResponse con los datos
            del índice y metadatos con los filtros aplicados.
    """
    dto = await service.get_indice_por_ocupacion(
        ocupacion=ocupacion,
        pais=filtros.pais,
        sector=filtros.sector,
        periodo=filtros.periodo,
    )

    data = IndiceEmpleabilidadDataSchema(
        ocupacion_id=dto.ocupacion_id,
        ocupacion_nombre=dto.ocupacion_nombre,
        score=dto.score,
        nivel=dto.nivel,
        dimensiones=[
            DimensionIndiceSchema(
                nombre=dim.nombre,
                valor=dim.valor,
                peso=dim.peso,
                descripcion=dim.descripcion,
            )
            for dim in dto.dimensiones
        ],
        tipo=dto.tipo,
        fuente=dto.fuente,
        fecha_actualizacion=dto.fecha_actualizacion,
        metodologia=dto.metodologia,
        pais=dto.pais,
        sector=dto.sector,
        periodo=dto.periodo,
        evolucion=[
            EvolucionIndicePuntoSchema(
                periodo=evo.periodo,
                valor=evo.valor,
            )
            for evo in dto.evolucion
        ],
    )

    meta = ResponseMeta(
        total=1,
        extra={"filtros": filtros.model_dump()},
    )

    return create_success_response(
        data=data,
        message="Índice de Empleabilidad obtenido con éxito.",
        status_code=status.HTTP_200_OK,
        meta=meta,
    )
