"""Controlador y endpoints asociados al módulo de ingesta de datos."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import provide_file_upload_service
from app.api.v1.schemas.ingesta_schema import (
    FileUploadData,
    FileUploadResponseSchema,
)
from app.api.v1.schemas.response_schema import ApiResponse, create_success_response
from app.application.services.file_upload_service import FileUploadService
from app.core.constants import INGESTA_ROUTE, INGESTA_UPLOAD_ROUTE

ingesta_router = APIRouter(
    prefix=INGESTA_ROUTE,
    tags=["Ingesta"],
)


@ingesta_router.post(
    INGESTA_UPLOAD_ROUTE,
    response_model=FileUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Subir y almacenar archivo CSV para ingesta",
    description=(
        "Recibe un archivo tabular multipart en formato CSV, ejecuta validaciones "
        "estrictas de formato, contenido y tamaño máximo, y lo persiste en disco "
        "de manera asíncrona no bloqueante."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Archivo validado y persistido con éxito.",
            "model": FileUploadResponseSchema,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": (
                "Violación de regla de dominio (formato no CSV, archivo vacío, "
                "tamaño excedido o contenido binario no admisible)."
            ),
            "model": ApiResponse,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Error de validación sintáctica de la petición HTTP.",
            "model": ApiResponse,
        },
    },
)
async def upload_csv_file(
    file: Annotated[
        UploadFile,
        File(description="Archivo en formato CSV para ingesta de datos"),
    ],
    upload_service: Annotated[
        FileUploadService,
        Depends(provide_file_upload_service),
    ],
) -> FileUploadResponseSchema:
    """Procesa la subida y persistencia de un archivo CSV de datos.

    Args:
        file: Archivo multipart enviado por el cliente.
        upload_service: Servicio de aplicación para validación y persistencia.

    Returns:
        FileUploadResponseSchema: Envoltorio estándar ApiResponse con metadatos.
    """
    file_bytes = await file.read()

    result_dto = await upload_service.upload_csv(
        filename=file.filename or "",
        content=file_bytes,
        content_type=file.content_type,
    )

    data = FileUploadData(
        filename=result_dto.filename,
        original_filename=result_dto.original_filename,
        file_path=result_dto.file_path,
        size_bytes=result_dto.size_bytes,
        content_type=result_dto.content_type,
    )

    return create_success_response(
        data=data,
        message="Archivo CSV subido y persistido con éxito.",
        status_code=status.HTTP_201_CREATED,
    )
