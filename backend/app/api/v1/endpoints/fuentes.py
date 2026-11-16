"""Controlador y endpoints asociados a la gestión y consulta de fuentes de datos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import provide_fuente_service
from app.api.v1.schemas.fuentes_schema import (
    FuenteCreateSchema,
    FuenteItemSchema,
    FuenteResponseSchema,
    FuentesResponseSchema,
)
from app.api.v1.schemas.response_schema import ResponseMeta, create_success_response
from app.application.services.fuentes_service import FuenteService
from app.core.constants import FUENTE_ROUTE, OPENAPI_TAG_FUENTE, FuenteEstado

fuentes_router = APIRouter(prefix=FUENTE_ROUTE, tags=[OPENAPI_TAG_FUENTE])


@fuentes_router.get(
    "",
    response_model=FuentesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar todas las fuentes",
    description="Retorna el listado completo de fuentes de datos del sistema.",
)
async def get_all_fuentes(
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuentesResponseSchema:
    """Obtiene todas las fuentes registradas en el sistema.

    Args:
        service: Servicio de aplicación para gestión de fuentes inyectado.

    Returns:
        FuentesResponseSchema: Envoltorio ApiResponse con la lista de fuentes.
    """
    fuentes = await service.get_all_fuentes()
    return create_success_response(
        data=fuentes,
        message="Fuentes obtenidas con éxito.",
        status_code=status.HTTP_200_OK,
        meta=ResponseMeta(total=len(fuentes)),
    )


@fuentes_router.get(
    "/{fuente_id}",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar fuente por id",
    description="Obtiene el detalle de una fuente específica por su identificador.",
)
async def get_fuente_by_id(
    fuente_id: int,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """Obtiene una fuente específica por su ID.

    Args:
        fuente_id: Identificador numérico de la fuente.
        service: Servicio de fuentes inyectado.

    Returns:
        FuenteResponseSchema: Envoltorio ApiResponse con la fuente encontrada.

    Raises:
        HTTPException: Si la fuente no existe en la base de datos (404).
    """
    fuente = await service.get_fuente_by_id(fuente_id)
    if fuente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuente con ID {fuente_id} no encontrada.",
        )
    return create_success_response(
        data=fuente,
        message="Fuente obtenida con éxito.",
        status_code=status.HTTP_200_OK,
    )


@fuentes_router.get(
    "/estado/{estado}",
    response_model=FuentesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar fuentes por estado",
    description=(
        "Obtiene todas las fuentes que coinciden con un estado operativo específico."
    ),
)
async def get_fuentes_by_estado(
    estado: FuenteEstado,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuentesResponseSchema:
    """Obtiene todas las fuentes filtradas por su estado.

    Args:
        estado: Estado operativo solicitado (activa, desactualizada, no_disponible).
        service: Servicio de fuentes inyectado.

    Returns:
        FuentesResponseSchema: Envoltorio ApiResponse con las fuentes coincidentes.
    """
    fuentes = await service.get_fuentes_by_estado(estado)
    return create_success_response(
        data=fuentes,
        message="Fuentes obtenidas con éxito.",
        status_code=status.HTTP_200_OK,
        meta=ResponseMeta(total=len(fuentes)),
    )


@fuentes_router.post(
    "",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva fuente",
    description="Registra una nueva fuente de datos en el sistema.",
)
async def create_fuente(
    fuente_data: FuenteCreateSchema,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """Crea una nueva fuente en el sistema.

    Args:
        fuente_data: Carga útil para crear la fuente.
        service: Servicio de fuentes inyectado.

    Returns:
        FuenteResponseSchema: Envoltorio ApiResponse con la fuente creada.
    """
    new_fuente = await service.create_fuente(fuente_data)
    return create_success_response(
        data=new_fuente,
        message="Fuente creada con éxito.",
        status_code=status.HTTP_201_CREATED,
    )


@fuentes_router.put(
    "/{fuente_id}",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar fuente existente",
    description="Actualiza los atributos de una fuente existente en el sistema.",
)
async def update_fuente(
    fuente_id: int,
    fuente_data: FuenteItemSchema,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """Actualiza una fuente existente en el sistema.

    Args:
        fuente_id: ID de la fuente a actualizar.
        fuente_data: Datos actualizados de la fuente.
        service: Servicio de fuentes inyectado.

    Returns:
        FuenteResponseSchema: Envoltorio ApiResponse con la fuente actualizada.

    Raises:
        HTTPException: Si el ID de la ruta no coincide con el cuerpo (400).
    """
    if fuente_id != fuente_data.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El ID de la fuente en la URL no coincide con el ID en el cuerpo"
                " de la solicitud."
            ),
        )

    updated_fuente = await service.update_fuente(fuente_id, fuente_data)
    return create_success_response(
        data=updated_fuente,
        message="Fuente actualizada con éxito.",
        status_code=status.HTTP_200_OK,
    )


@fuentes_router.delete(
    "/{fuente_id}",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Eliminar fuente existente",
    description="Elimina una fuente existente en el sistema.",
)
async def delete_fuente(
    fuente_id: int,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """Elimina una fuente existente en el sistema.

    Args:
        fuente_id: Identificador numérico de la fuente a eliminar.
        service: Servicio de fuentes inyectado.

    Returns:
        FuenteResponseSchema: Envoltorio ApiResponse confirmando la eliminación.
    """
    await service.delete_fuente(fuente_id)
    return create_success_response(
        data=None,
        message="Fuente eliminada con éxito.",
        status_code=status.HTTP_200_OK,
    )
