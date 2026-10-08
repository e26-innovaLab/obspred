"""Esquemas Pydantic de la versión 1 de la API."""

from app.api.v1.schemas.health_schema import (
    HealthDataSchema,
    HealthResponseSchema,
)
from app.api.v1.schemas.indicadores_schema import (
    IndicadoresFilterSchema,
    IndicadoresResponseSchema,
    IndicadorItemSchema,
)
from app.api.v1.schemas.indice_empleabilidad_schema import (
    DimensionIndiceSchema,
    EvolucionIndicePuntoSchema,
    IndiceEmpleabilidadDataSchema,
    IndiceEmpleabilidadFilterSchema,
    IndiceEmpleabilidadResponseSchema,
)
from app.api.v1.schemas.ingesta_schema import (
    FileUploadData,
    FileUploadResponseSchema,
)
from app.api.v1.schemas.prueba_schema import (
    PruebaItemData,
    PruebaPayloadSchema,
    PruebaResponseSchema,
)
from app.api.v1.schemas.response_schema import (
    ApiResponse,
    ErrorDetail,
    ResponseMeta,
    create_error_response,
    create_success_response,
)

__all__ = [
    "ApiResponse",
    "DimensionIndiceSchema",
    "ErrorDetail",
    "EvolucionIndicePuntoSchema",
    "FileUploadData",
    "FileUploadResponseSchema",
    "HealthDataSchema",
    "HealthResponseSchema",
    "IndicadorItemSchema",
    "IndicadoresFilterSchema",
    "IndicadoresResponseSchema",
    "IndiceEmpleabilidadDataSchema",
    "IndiceEmpleabilidadFilterSchema",
    "IndiceEmpleabilidadResponseSchema",
    "PruebaItemData",
    "PruebaPayloadSchema",
    "PruebaResponseSchema",
    "ResponseMeta",
    "create_error_response",
    "create_success_response",
]
