"""Controladores de endpoints de la versión 1."""

from app.api.v1.endpoints.health import health_router
from app.api.v1.endpoints.indicadores import indicadores_router
from app.api.v1.endpoints.ingesta import ingesta_router
from app.api.v1.endpoints.prueba_endpoint_borrar import prueba_router
from app.api.v1.endpoints import tendencias

__all__ = [
    "health_router",
    "indicadores_router",
    "ingesta_router",
    "prueba_router",
    ""
]
