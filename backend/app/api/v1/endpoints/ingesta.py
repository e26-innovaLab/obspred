"""Controlador y endpoints asociados al módulo de ingesta y sincronización de datos."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.dependencies import (
    provide_file_upload_service,
    provide_world_bank_sync_service,
)
from app.api.v1.schemas.ingesta_schema import (
    FileUploadData,
    FileUploadResponseSchema,
    SyncExternalDataRequestSchema,
    SyncExternalDataResponseData,
    SyncExternalDataResponseSchema,
)
from app.api.v1.schemas.response_schema import (
    ApiResponse,
    ErrorDetail,
    create_error_response,
    create_success_response,
)
from app.application.services.external_sync_service import ExternalSyncService
from app.application.services.file_upload_service import FileUploadService
from app.core.constants import (
    INGESTA_ROUTE,
    INGESTA_SYNC_ROUTE,
    INGESTA_UPLOAD_ROUTE,
)

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


@ingesta_router.post(
    f"{INGESTA_SYNC_ROUTE}/world-bank",
    response_model=SyncExternalDataResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Sincronizar indicadores oficiales desde World Bank Indicators API",
    description=(
        "Ejecuta extracción y persistencia idempotente de indicadores "
        "macroeconómicos y laborales oficiales desde la API del Banco Mundial "
        "para Argentina, Uruguay y Chile."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Sincronización completada exitosamente.",
            "model": SyncExternalDataResponseSchema,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error de persistencia o conexión con base de datos.",
            "model": ApiResponse,
        },
        status.HTTP_502_BAD_GATEWAY: {
            "description": "Error al comunicarse con la API remota externa.",
            "model": ApiResponse,
        },
    },
)
async def sync_world_bank_indicators(
    sync_service: Annotated[
        ExternalSyncService,
        Depends(provide_world_bank_sync_service),
    ],
    payload: Optional[SyncExternalDataRequestSchema] = None,
) -> SyncExternalDataResponseSchema | JSONResponse:
    """Sincroniza indicadores oficiales del Banco Mundial.

    Args:
        sync_service: Servicio de orquestación de ingesta externa inyectado.
        payload: Parámetros opcionales para restringir países o indicadores.

    Returns:
        SyncExternalDataResponseSchema | JSONResponse: Resultado exitoso
            o ApiResponse de error estándar.
    """
    paises = payload.paises if payload else None
    indicadores = payload.indicadores if payload else None
    periodo_desde = payload.periodo_desde if payload else None
    periodo_hasta = payload.periodo_hasta if payload else None

    result_dto = await sync_service.sync_data(
        paises=paises,
        indicadores=indicadores,
        periodo_desde=periodo_desde,
        periodo_hasta=periodo_hasta,
    )

    if result_dto.status == "failed":
        err_msg = (
            result_dto.error_message
            or "Ocurrió un error inesperado durante la sincronización."
        )
        is_db_err = any(
            tok in err_msg
            for tok in [
                "Connect call failed",
                "OperationalError",
                "database",
                "5432",
            ]
        )
        http_status = (
            status.HTTP_500_INTERNAL_SERVER_ERROR
            if is_db_err
            else status.HTTP_502_BAD_GATEWAY
        )
        err_code = (
            "DATABASE_CONNECTION_ERROR"
            if is_db_err
            else "EXTERNAL_SERVICE_ERROR"
        )
        error_response = create_error_response(
            message=f"Fallo en la sincronización de '{result_dto.source}'.",
            status_code=http_status,
            errors=[
                ErrorDetail(
                    code=err_code,
                    detail=err_msg,
                    field="source",
                )
            ],
        )
        return JSONResponse(
            status_code=http_status,
            content=error_response.model_dump(mode="json"),
        )

    response_data = SyncExternalDataResponseData(
        source=result_dto.source,
        status=result_dto.status,
        total_fetched=result_dto.total_fetched,
        total_persisted=result_dto.total_persisted,
        execution_time_seconds=result_dto.execution_time_seconds,
        countries_synced=result_dto.countries_synced,
        indicators_synced=result_dto.indicators_synced,
        error_message=result_dto.error_message,
    )

    msg = f"Sincronización de '{result_dto.source}' exitosa."
    return create_success_response(
        data=response_data,
        message=msg,
        status_code=status.HTTP_200_OK,
    )
