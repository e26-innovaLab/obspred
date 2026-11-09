"""Controladores de endpoints de la versión 1."""

from app.api.v1.endpoints.alertas import alertas_router
from app.api.v1.endpoints.brechas import brechas_router
from app.api.v1.endpoints.catalogo import catalogo_router
from app.api.v1.endpoints.health import health_router
from app.api.v1.endpoints.indicadores import indicadores_router
from app.api.v1.endpoints.indice_empleabilidad import indice_empleabilidad_router
from app.api.v1.endpoints.ingesta import ingesta_router
from app.api.v1.endpoints.metricas import metricas_router
from app.api.v1.endpoints.tendencias import tendencias_router

__all__ = [
    "alertas_router",
    "brechas_router",
    "catalogo_router",
    "health_router",
    "indicadores_router",
    "indice_empleabilidad_router",
    "ingesta_router",
    "metricas_router",
    "tendencias_router",
]
