"""Enrutador central para la versión 1 de la API."""

from fastapi import APIRouter

from app.api.v1.endpoints.alertas import alertas_router
from app.api.v1.endpoints.brechas import brechas_router
from app.api.v1.endpoints.catalogo import catalogo_router
from app.api.v1.endpoints.fuentes import fuentes_router
from app.api.v1.endpoints.health import health_router
from app.api.v1.endpoints.indicadores import indicadores_router
from app.api.v1.endpoints.indice_empleabilidad import (
    indice_empleabilidad_router,
)
from app.api.v1.endpoints.ingesta import ingesta_router
from app.api.v1.endpoints.metricas import metricas_router
from app.api.v1.endpoints.tendencias import tendencias_router

api_v1_router = APIRouter()

# Registro modular de submódulos de la API
api_v1_router.include_router(health_router)
api_v1_router.include_router(indicadores_router)
api_v1_router.include_router(indice_empleabilidad_router)
api_v1_router.include_router(ingesta_router)
api_v1_router.include_router(brechas_router)
api_v1_router.include_router(tendencias_router)
api_v1_router.include_router(metricas_router)
api_v1_router.include_router(catalogo_router)
api_v1_router.include_router(alertas_router)
api_v1_router.include_router(fuentes_router)
