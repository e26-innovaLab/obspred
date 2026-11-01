from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import provide_fuente_service
from app.api.v1.schemas.fuentes_schema import (
    FuenteCreateSchema,
    FuenteResponseSchema,
    FuentesResponseSchema,
    FuenteItemSchema,
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
    
    fuentes = await service.get_all_fuentes()
    response_meta = ResponseMeta(
        status_code=status.HTTP_200_OK, message="Fuentes obtenidas con éxito."
    )
    return create_success_response(data=fuentes, meta=response_meta)
    

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
    
    fuentes = await service.get_fuentes_by_estado(estado)
    response_meta = ResponseMeta(
        status_code=status.HTTP_200_OK, message="Fuentes obtenidas con éxito."
    )
    return create_success_response(data=fuentes, meta=response_meta)
    


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
    
    new_fuente = await service.create_fuente(fuente_data)
    response_meta = ResponseMeta(
        status_code=status.HTTP_201_CREATED, message="Fuente creada con éxito."
    )
    return create_success_response(data=new_fuente, meta=response_meta)
    



@fuentes_router.put(
    
        "/{fuente_id}",
        response_model=FuenteResponseSchema,
        status_code=status.HTTP_200_OK,
        summary="actualizar fuente existente",
        
    )
async def update_fuente(
    fuente_id: int,
    fuente_data: FuenteItemSchema,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """
    Actualiza una fuente existente en el sistema.
    """
    if fuente_id != fuente_data.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la fuente en la URL no coincide con el ID en el cuerpo de la solicitud.",
        )
    
    
    updated_fuente = await service.update_fuente(fuente_id, fuente_data)

    response_meta = ResponseMeta(
        status_code=status.HTTP_200_OK, message="Fuente actualizada con éxito."
    )
    return create_success_response(data=updated_fuente, meta=response_meta)
   



@fuentes_router.delete(
    "/{fuente_id}",
    response_model=FuenteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="eliminar fuente existente",
)
async def delete_fuente(
    fuente_id: int,
    service: Annotated[FuenteService, Depends(provide_fuente_service)],
) -> FuenteResponseSchema:
    """
    Elimina una fuente existente en el sistema.
    """
    
    await service.delete_fuente(fuente_id)
    response_meta = ResponseMeta(
        status_code=status.HTTP_200_OK, message="Fuente eliminada con éxito."
    )
    return create_success_response(data=None, meta=response_meta)