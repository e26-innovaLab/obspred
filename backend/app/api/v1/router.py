"""Enrutador central para la versión 1 de la API."""

from fastapi import APIRouter

from app.api.v1.endpoints.health import health_router
from app.api.v1.endpoints.ingesta import ingesta_router
from app.api.v1.endpoints.prueba_endpoint_borrar import prueba_router

api_v1_router = APIRouter()

# Registro modular de submódulos de la API
api_v1_router.include_router(health_router)
api_v1_router.include_router(ingesta_router)
api_v1_router.include_router(prueba_router)
