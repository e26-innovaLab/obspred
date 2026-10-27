from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import provide_fuente_service
from app.api.v1.schemas.fuentes_schema import (
    FuenteCreateSchema,
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
    summary="consultar todas las fuentes",
)
async def get_all_fuentes(
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuentesResponseSchema:
    """
    Obtiene todas las fuentes disponibles en el sistema.
    """
    try:
        fuentes = await service.get_all_fuentes()
        response_meta = ResponseMeta(
            status_code=status.HTTP_200_OK, message="Fuentes obtenidas con éxito."
        )
        return create_success_response(data=fuentes, meta=response_meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las fuentes: {str(e)}",
        ) from e


@fuentes_router.get(
    "/{fuente_id}",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="consultar fuente por id",
)
async def get_fuente_by_id(
    fuente_id: int, service: Annotated[FuenteService, Depends(provide_fuente_service)]
) -> FuenteResponseSchema:
    """
    Obtiene una fuente específica por su ID.
    """
    try:
        fuente = await service.get_fuente_by_id(fuente_id)
        if fuente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fuente con ID {fuente_id} no encontrada.",
            )
        response_meta = ResponseMeta(
            status_code=status.HTTP_200_OK, message="Fuente obtenida con éxito."
        )
        return create_success_response(data=fuente, meta=response_meta)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la fuente: {str(e)}",
        )from e


@fuentes_router.get(
    "/estado/{estado}",
    response_model=FuentesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="consultar fuentes por estado",
)
async def get_fuentes_by_estado(
    estado: FuenteEstado,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuentesResponseSchema:
    """
    Obtiene todas las fuentes que coinciden con un estado específico.
    """
    try:
        fuentes = await service.get_fuentes_by_estado(estado)
        response_meta = ResponseMeta(
            status_code=status.HTTP_200_OK, message="Fuentes obtenidas con éxito."
        )
        return create_success_response(data=fuentes, meta=response_meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las fuentes por estado: {str(e)}",
        )from e


@fuentes_router.post(
    "",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="crear nueva fuente",
)
async def create_fuente(
    fuente_data: FuenteCreateSchema,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """
    Crea una nueva fuente en el sistema.
    """
    try:
        new_fuente = await service.create_fuente(fuente_data)
        response_meta = ResponseMeta(
            status_code=status.HTTP_201_CREATED, message="Fuente creada con éxito."
        )
        return create_success_response(data=new_fuente, meta=response_meta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la fuente: {str(e)}",
        )from e
