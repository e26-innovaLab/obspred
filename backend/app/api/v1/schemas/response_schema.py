"""Esquema estándar genérico para todas las respuestas REST de la API.

Implementa el patrón de envoltorio unificado (Envelope Pattern) para asegurar
consistencia estructural tanto en respuestas exitosas como en errores.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (
    DEFAULT_ERROR_MESSAGE,
    DEFAULT_SUCCESS_MESSAGE,
)

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detalle puntual de un error de validación o excepción.

    Attributes:
        code: Código alfanumérico estandarizado del error
            (ej. VALIDATION_ERROR, NOT_FOUND).
        detail: Descripción legible del problema.
        field: Campo del payload que provocó el error si corresponde.
    """

    model_config = ConfigDict(frozen=True)

    code: str = Field(
        ...,
        description="Código de clasificación del error",
    )
    detail: str = Field(
        ...,
        description="Mensaje descriptivo del error",
    )
    field: Optional[str] = Field(
        default=None,
        description="Nombre del parámetro o campo inválido si aplica",
    )


class ResponseMeta(BaseModel):
    """Metadatos optativos para paginación, filtros o contexto de ejecución.

    Attributes:
        page: Número de página actual en listados paginados.
        per_page: Cantidad de elementos por página.
        total: Total general de registros disponibles.
        extra: Información contextual adicional.
    """

    model_config = ConfigDict(frozen=True)

    page: Optional[int] = Field(default=None, description="Número de página actual")
    per_page: Optional[int] = Field(default=None, description="Tamaño de la página")
    total: Optional[int] = Field(
        default=None, description="Cantidad total de registros"
    )
    extra: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadatos adicionales de la consulta"
    )


class ApiResponse(BaseModel, Generic[T]):
    """Envoltorio estándar para todas las respuestas REST del Observatorio.

    Garantiza que toda respuesta (2xx, 4xx, 5xx) mantenga la misma estructura JSON.

    Attributes:
        success: Booleano que indica si la solicitud concluyó favorablemente.
        status_code: Código numérico HTTP de la respuesta.
        message: Mensaje legible orientado al usuario o cliente.
        data: Carga útil con la información devuelta (tipada genéricamente).
        errors: Lista de errores o inconsistencias si la operación falló.
        meta: Metadatos adicionales de paginación o trazabilidad.
        timestamp: Marca de tiempo UTC de generación de la respuesta.
    """

    model_config = ConfigDict(frozen=True)

    success: bool = Field(
        default=True,
        description="Indicador de éxito de la operación",
    )
    status_code: int = Field(
        default=200,
        description="Código de estado HTTP",
    )
    message: str = Field(
        default=DEFAULT_SUCCESS_MESSAGE,
        description="Mensaje resumen de la operación",
    )
    data: Optional[T] = Field(
        default=None,
        description="Payload o cuerpo principal del resultado",
    )
    errors: Optional[List[ErrorDetail]] = Field(
        default=None,
        description="Listado detallado de errores en caso de fallo",
    )
    meta: Optional[ResponseMeta] = Field(
        default=None,
        description="Metadatos auxiliares de la respuesta",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora UTC de la respuesta",
    )

    @classmethod
    def create_success(
        cls,
        data: Optional[T] = None,
        message: str = DEFAULT_SUCCESS_MESSAGE,
        status_code: int = 200,
        meta: Optional[ResponseMeta] = None,
    ) -> "ApiResponse[T]":
        """Crea una respuesta estándar exitosa."""
        return cls(
            success=True,
            status_code=status_code,
            message=message,
            data=data,
            meta=meta,
            errors=None,
        )

    @classmethod
    def create_error(
        cls,
        message: str = DEFAULT_ERROR_MESSAGE,
        status_code: int = 400,
        errors: Optional[List[ErrorDetail]] = None,
        meta: Optional[ResponseMeta] = None,
    ) -> "ApiResponse[None]":
        """Crea una respuesta estándar de error."""
        return cls(
            success=False,
            status_code=status_code,
            message=message,
            data=None,
            errors=errors,
            meta=meta,
        )


def create_success_response(
    data: Optional[T] = None,
    message: str = DEFAULT_SUCCESS_MESSAGE,
    status_code: int = 200,
    meta: Optional[ResponseMeta] = None,
) -> ApiResponse[T]:
    """Función constructora genérica para inferir con tipado estricto ApiResponse[T].

    Resuelve diagnósticos de tipos desconocidos en Pylance infiriendo 'T'
    directamente desde el parámetro 'data'.
    """
    return ApiResponse[T](
        success=True,
        status_code=status_code,
        message=message,
        data=data,
        meta=meta,
        errors=None,
    )


def create_error_response(
    message: str = DEFAULT_ERROR_MESSAGE,
    status_code: int = 400,
    errors: Optional[List[ErrorDetail]] = None,
    meta: Optional[ResponseMeta] = None,
) -> ApiResponse[None]:
    """Función constructora para respuestas estándar de error fuertemente tipadas."""
    return ApiResponse[None](
        success=False,
        status_code=status_code,
        message=message,
        data=None,
        errors=errors,
        meta=meta,
    )
