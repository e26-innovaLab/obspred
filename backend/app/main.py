"""Punto de entrada principal para la aplicación FastAPI del backend.

Configura middlewares de seguridad, rutas centrales, estandarización de respuestas
y manejadores globales de excepciones bajo el esquema ApiResponse.
"""

from typing import Any, Dict
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.router import api_v1_router
from app.api.v1.schemas.response_schema import (
    ApiResponse,
    ErrorDetail,
    create_error_response,
    create_success_response,
)
from app.core.config import settings
from app.core.constants import (
    DEFAULT_ERROR_MESSAGE,
    INTERNAL_SERVER_ERROR_MESSAGE,
    ROOT_ROUTE,
)
from app.core.logging import logger
from app.domain.exceptions.base import DomainException, EntityNotFoundException


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de errores para formatear toda excepción con ApiResponse.

    Args:
        app: Instancia de la aplicación FastAPI.
    """

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundException
    ) -> JSONResponse:
        """Maneja entidades de dominio no localizadas (HTTP 404)."""
        error_response = create_error_response(
            message=exc.message,
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[
                ErrorDetail(
                    code="ENTITY_NOT_FOUND",
                    detail=exc.message,
                    field=exc.entity_name,
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        """Maneja violaciones de reglas de negocio del dominio (HTTP 400)."""
        error_response = create_error_response(
            message=exc.message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=[
                ErrorDetail(
                    code="DOMAIN_RULE_VIOLATION",
                    detail=exc.message,
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Maneja errores de validación de sintaxis o tipos en peticiones entrantes (HTTP 422)."""
        errors = [
            ErrorDetail(
                code="VALIDATION_ERROR",
                detail=err.get("msg", "Error de validación"),
                field=".".join(str(loc) for loc in err.get("loc", [])),
            )
            for err in exc.errors()
        ]
        error_response = create_error_response(
            message="Error de validación en los parámetros enviados.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            errors=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Maneja excepciones HTTP estándar de Starlette/FastAPI."""
        detail_msg = str(exc.detail) if exc.detail else DEFAULT_ERROR_MESSAGE
        error_response = create_error_response(
            message=detail_msg,
            status_code=exc.status_code,
            errors=[
                ErrorDetail(
                    code="HTTP_EXCEPTION",
                    detail=detail_msg,
                )
            ],
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Captura cualquier excepción no controlada devolviendo HTTP 500 estándar."""
        logger.error(f"Excepción no controlada: {exc}", exc_info=True)
        error_response = create_error_response(
            message=INTERNAL_SERVER_ERROR_MESSAGE,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[
                ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    detail="Consulte con el equipo de soporte técnico.",
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json"),
        )


def create_application() -> FastAPI:
    """Fábrica de inicialización de la aplicación FastAPI.

    Returns:
        FastAPI: Instancia de la aplicación configurada con rutas y middlewares.
    """
    application = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Configuración de CORS
    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Manejadores globales de errores con estándar ApiResponse
    register_exception_handlers(application)

    # Ruta raíz básica estandarizada
    @application.get(
        ROOT_ROUTE,
        response_model=ApiResponse[Dict[str, Any]],
        status_code=status.HTTP_200_OK,
        tags=["Root"],
        summary="Ruta raíz del backend",
        description="Retorna el estado base de la API bajo el formato estándar ApiResponse.",
    )
    async def root_endpoint() -> ApiResponse[Dict[str, Any]]:
        """Endpoint raíz informativo.

        Returns:
            ApiResponse: Envoltorio estándar confirmando la disponibilidad del backend.
        """
        payload = {
            "name": settings.app_name,
            "status": "online",
            "docs": "/docs" if settings.debug else "disabled",
        }
        return create_success_response(
            data=payload,
            message="Backend del Observatorio en funcionamiento.",
            status_code=status.HTTP_200_OK,
        )

    # Registro de rutas de versión 1
    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    return application


# Aplicación instanciada para Uvicorn
app = create_application()
