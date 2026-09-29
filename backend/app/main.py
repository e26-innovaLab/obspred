"""Punto de entrada principal para la aplicación FastAPI del backend.

Configura middlewares de seguridad, rutas centrales y documentación interactiva OpenAPI.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.constants import ROOT_ROUTE


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

    # Ruta raíz básica
    @application.get(
        ROOT_ROUTE,
        status_code=status.HTTP_200_OK,
        tags=["Root"],
        summary="Ruta raíz del backend",
    )
    async def root_endpoint() -> dict:
        """Endpoint raíz informativo.

        Returns:
            dict: Mensaje de confirmación del estado operativo de la API.
        """
        return {
            "name": settings.app_name,
            "status": "online",
            "docs": "/docs" if settings.debug else "disabled",
        }

    # Registro de rutas de versión 1
    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    return application


# Aplicación instanciada para Uvicorn
app = create_application()
