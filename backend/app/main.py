"""Punto de entrada principal para la aplicación FastAPI del backend.

Configura middlewares de seguridad, rutas centrales, estandarización de respuestas
y manejadores globales de excepciones bajo el esquema ApiResponse.
"""

import traceback
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import InterfaceError, OperationalError
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
    DATABASE_UNAVAILABLE_DETAIL,
    DATABASE_UNAVAILABLE_MESSAGE,
    DEFAULT_APP_VERSION,
    DEFAULT_ERROR_MESSAGE,
    DOCS_ROUTE,
    INTERNAL_SERVER_ERROR_MESSAGE,
    JSON_SERIALIZATION_MODE,
    OPENAPI_TAG_ROOT,
    REDOC_ROUTE,
    ROOT_ROUTE,
    ApiErrorCode,
)
from app.core.logging import logger
from app.domain.exceptions.base import (
    DatabaseConnectionException,
    DomainException,
    EntityNotFoundException,
)
from app.infrastructure.persistence.database import dispose_database


def is_database_connection_error(exc: BaseException) -> bool:
    """Determina si una excepción corresponde a un fallo de conexión o BD offline.

    Args:
        exc: Excepción capturada.

    Returns:
        bool: True si la excepción corresponde a indisponibilidad de BD.
    """
    if isinstance(
        exc,
        (
            DatabaseConnectionException,
            OperationalError,
            InterfaceError,
            ConnectionRefusedError,
            ConnectionError,
        ),
    ):
        return True

    db_keywords = (
        "connect call failed",
        "10061",  # WSAECONNREFUSED en Windows
        "errno 111",  # ECONNREFUSED en Linux
        "errno 61",  # ECONNREFUSED en macOS
        "5432",  # Puerto estándar de PostgreSQL
        "connection refused",
        "could not connect",
        "cannot connect",
        "connection to server",
        "is the server running",
        "operationalerror",
        "pool_timeout",
        "timeout expired",
        "database is locked",
        "server closed the connection unexpectedly",
        "database offline",
        "connection reset",
        "asyncpg",
        "psycopg",
        "aiosqlite",
        "targetserverattributenotmatched",
    )

    curr: BaseException | None = exc
    visited: set[int] = set()
    while curr is not None and id(curr) not in visited:
        visited.add(id(curr))
        if isinstance(
            curr,
            (
                DatabaseConnectionException,
                OperationalError,
                InterfaceError,
                ConnectionRefusedError,
                ConnectionError,
            ),
        ):
            return True

        curr_str = str(curr).lower()
        if any(kw in curr_str for kw in db_keywords):
            return True

        # Inspección del traceback para detectar frames originados en persistencia
        tb = getattr(curr, "__traceback__", None)
        if tb:
            frames = traceback.extract_tb(tb)
            db_markers = (
                "sqlalchemy",
                "asyncpg",
                "aiosqlite",
                "persistence",
                "database.py",
            )
            in_db_layer = any(
                any(marker in f.filename.lower() for marker in db_markers)
                for f in frames
            )
            if in_db_layer and isinstance(
                curr, (OSError, ConnectionError, TimeoutError, RuntimeError)
            ):
                return True

        curr = getattr(curr, "__cause__", None) or getattr(curr, "__context__", None)

    return False


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de errores para formatear toda
    excepción con ApiResponse.

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
                    code=ApiErrorCode.ENTITY_NOT_FOUND,
                    detail=exc.message,
                    field=exc.entity_name,
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
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
                    code=ApiErrorCode.DOMAIN_RULE_VIOLATION,
                    detail=exc.message,
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Maneja errores de validación de sintaxis o tipos en peticiones
        entrantes (HTTP 422).
        """
        errors = [
            ErrorDetail(
                code=ApiErrorCode.VALIDATION_ERROR,
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
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
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
                    code=ApiErrorCode.HTTP_EXCEPTION,
                    detail=detail_msg,
                )
            ],
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )

    @app.exception_handler(DatabaseConnectionException)
    async def database_connection_handler(
        request: Request, exc: DatabaseConnectionException
    ) -> JSONResponse:
        """Maneja fallos de conectividad con la base de datos (HTTP 503)."""
        logger.error(
            f"Fallo de conexión a la base de datos: {exc.message}", exc_info=True
        )
        error_response = create_error_response(
            message=exc.message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            errors=[
                ErrorDetail(
                    code=ApiErrorCode.DATABASE_CONNECTION_ERROR,
                    detail=exc.detail,
                    field="database",
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )

    @app.exception_handler(OperationalError)
    async def database_operational_handler(
        request: Request, exc: OperationalError
    ) -> JSONResponse:
        """Maneja errores operacionales de SQLAlchemy por BD offline (HTTP 503)."""
        logger.error(
            f"Error operacional de base de datos (offline/desconectada): {exc}",
            exc_info=True,
        )
        error_response = create_error_response(
            message=DATABASE_UNAVAILABLE_MESSAGE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            errors=[
                ErrorDetail(
                    code=ApiErrorCode.DATABASE_CONNECTION_ERROR,
                    detail=DATABASE_UNAVAILABLE_DETAIL,
                    field="database",
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )

    @app.exception_handler(OSError)
    async def os_error_handler(request: Request, exc: OSError) -> JSONResponse:
        """Maneja fallos de sockets a nivel de SO (ej. PostgreSQL offline)."""
        logger.error(
            f"Fallo de socket u OSError del sistema operativo: {exc}", exc_info=True
        )
        if is_database_connection_error(exc):
            error_response = create_error_response(
                message=DATABASE_UNAVAILABLE_MESSAGE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                errors=[
                    ErrorDetail(
                        code=ApiErrorCode.DATABASE_CONNECTION_ERROR,
                        detail=DATABASE_UNAVAILABLE_DETAIL,
                        field="database",
                    )
                ],
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
            )

        error_response = create_error_response(
            message=INTERNAL_SERVER_ERROR_MESSAGE,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[
                ErrorDetail(
                    code=ApiErrorCode.INTERNAL_SERVER_ERROR,
                    detail="Consulte con el equipo de soporte técnico.",
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Captura excepciones no controladas (HTTP 500 o 503 si es de BD)."""
        logger.error(f"Excepción no controlada: {exc}", exc_info=True)
        if is_database_connection_error(exc):
            error_response = create_error_response(
                message=DATABASE_UNAVAILABLE_MESSAGE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                errors=[
                    ErrorDetail(
                        code=ApiErrorCode.DATABASE_CONNECTION_ERROR,
                        detail=DATABASE_UNAVAILABLE_DETAIL,
                        field="database",
                    )
                ],
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
            )

        error_response = create_error_response(
            message=INTERNAL_SERVER_ERROR_MESSAGE,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[
                ErrorDetail(
                    code=ApiErrorCode.INTERNAL_SERVER_ERROR,
                    detail="Consulte con el equipo de soporte técnico.",
                )
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode=JSON_SERIALIZATION_MODE),
        )


def create_application() -> FastAPI:
    """Fábrica de inicialización de la aplicación FastAPI.

    Returns:
        FastAPI: Instancia de la aplicación configurada con rutas y middlewares.
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """Asegura la liberación del pool de conexiones antes de cerrar la app."""
        yield
        await dispose_database()

    application = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=DEFAULT_APP_VERSION,
        docs_url=DOCS_ROUTE if settings.debug else None,
        redoc_url=REDOC_ROUTE if settings.debug else None,
        lifespan=lifespan,
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
        response_model=ApiResponse[dict[str, Any]],
        status_code=status.HTTP_200_OK,
        tags=[OPENAPI_TAG_ROOT],
        summary="Ruta raíz del backend",
        description=(
            "Retorna el estado base de la API bajo el formato estándar ApiResponse."
        ),
    )
    async def root_endpoint() -> ApiResponse[dict[str, Any]]:
        """Endpoint raíz informativo.

        Returns:
            ApiResponse: Envoltorio estándar confirmando la disponibilidad del backend.
        """
        payload = {
            "name": settings.app_name,
            "status": "online",
            "docs": DOCS_ROUTE if settings.debug else "disabled",
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
