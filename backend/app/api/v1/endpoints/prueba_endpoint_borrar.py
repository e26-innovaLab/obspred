"""Controlador temporal para pruebas CRUD simuladas desde Postman.

Este endpoint expone todas las operaciones CRUD estándar (GET, POST, PUT, DELETE)
respondiendo con el envoltorio estándar ApiResponse para verificar la conectividad
y el estándar unificado de la API.
"""

from typing import Optional

from fastapi import APIRouter, Path, status

from app.api.v1.schemas.prueba_schema import (
    PruebaItemData,
    PruebaPayloadSchema,
    PruebaResponseSchema,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.constants import PRUEBA_ENDPOINT_BORRAR_ROUTE

prueba_router = APIRouter(
    prefix=PRUEBA_ENDPOINT_BORRAR_ROUTE,
    tags=["Prueba Endpoint Borrar"],
)


@prueba_router.get(
    "",
    response_model=PruebaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Listar recursos (CRUD: Read All)",
    description=(
        "Simula la lectura de una colección de recursos retornando el "
        "estándar ApiResponse."
    ),
)
async def list_simulated_items() -> PruebaResponseSchema:
    """Simula la obtención de un listado de elementos.

    Returns:
        PruebaResponseSchema: Respuesta estándar ApiResponse con datos de la operación.
    """
    item_data = PruebaItemData(method="GET")
    return create_success_response(
        data=item_data,
        message="Listado de recursos simulados consultado con éxito.",
        status_code=status.HTTP_200_OK,
    )


@prueba_router.get(
    "/{item_id}",
    response_model=PruebaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener un recurso por ID (CRUD: Read One)",
    description="Simula la lectura de un recurso específico por su identificador.",
)
async def get_simulated_item(
    item_id: str = Path(..., description="Identificador único del recurso"),
) -> PruebaResponseSchema:
    """Simula la consulta de un elemento puntual por ID.

    Args:
        item_id: Identificador enviado en la ruta.

    Returns:
        PruebaResponseSchema: Respuesta estándar ApiResponse con el ID consultado.
    """
    item_data = PruebaItemData(
        method="GET",
        item_id=item_id,
    )
    return create_success_response(
        data=item_data,
        message=f"Recurso con ID '{item_id}' consultado con éxito.",
        status_code=status.HTTP_200_OK,
    )


@prueba_router.post(
    "",
    response_model=PruebaResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un recurso (CRUD: Create)",
    description="Simula la creación de un nuevo recurso a partir de un payload JSON.",
)
async def create_simulated_item(
    payload: PruebaPayloadSchema,
) -> PruebaResponseSchema:
    """Simula la creación de un elemento.

    Args:
        payload: Datos de entrada enviados en el cuerpo de la petición.

    Returns:
        PruebaResponseSchema: Respuesta estándar con HTTP 201 y datos creados.
    """
    item_data = PruebaItemData(
        method="POST",
        payload=payload.model_dump(),
    )
    return create_success_response(
        data=item_data,
        message="Recurso simulado creado con éxito.",
        status_code=status.HTTP_201_CREATED,
    )


@prueba_router.put(
    "/{item_id}",
    response_model=PruebaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un recurso (CRUD: Update)",
    description="Simula la actualización completa de un recurso existente por su ID.",
)
async def update_simulated_item(
    item_id: str = Path(..., description="Identificador único del recurso a modificar"),
    payload: Optional[PruebaPayloadSchema] = None,
) -> PruebaResponseSchema:
    """Simula la actualización de un elemento por ID.

    Args:
        item_id: Identificador enviado en la ruta.
        payload: Datos opcionales con las modificaciones.

    Returns:
        PruebaResponseSchema: Respuesta estándar confirmando la actualización.
    """
    item_data = PruebaItemData(
        method="PUT",
        item_id=item_id,
        payload=payload.model_dump() if payload else None,
    )
    return create_success_response(
        data=item_data,
        message=f"Recurso con ID '{item_id}' actualizado con éxito.",
        status_code=status.HTTP_200_OK,
    )


@prueba_router.delete(
    "/{item_id}",
    response_model=PruebaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un recurso (CRUD: Delete)",
    description="Simula la eliminación de un recurso por su ID.",
)
async def delete_simulated_item(
    item_id: str = Path(..., description="Identificador único del recurso a eliminar"),
) -> PruebaResponseSchema:
    """Simula la baja de un elemento por ID.

    Args:
        item_id: Identificador del recurso a borrar.

    Returns:
        PruebaResponseSchema: Respuesta estándar confirmando la eliminación.
    """
    item_data = PruebaItemData(
        method="DELETE",
        item_id=item_id,
    )
    return create_success_response(
        data=item_data,
        message=f"Recurso con ID '{item_id}' eliminado con éxito.",
        status_code=status.HTTP_200_OK,
    )
