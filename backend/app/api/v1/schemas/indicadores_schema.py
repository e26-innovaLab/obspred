"""Esquemas Pydantic para la consulta y serialización de indicadores."""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.schemas.response_schema import ApiResponse


class IndicadoresFilterSchema(BaseModel):
    """Parámetros de consulta y filtrado jerárquico para indicadores.

    Normaliza y sanitiza automáticamente los filtros entrantes desde Query parameters,
    transformando cadenas vacías o compuestas únicamente por espacios en None.

    Attributes:
        pais: Filtro de país (raíz ineludible de la jerarquía, ej. ARG, URY, CHL).
        sector: Sector productivo o económico analizado.
        ocupacion: Ocupación analizada según taxonomía normalizada.
        desde: Límite temporal inicial del rango (ej. 2023, 2024-Q1).
        hasta: Límite temporal final del rango (ej. 2024, 2024-Q4).
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True,
        extra="forbid",
    )

    pais: Optional[str] = Field(
        default=None,
        description="Filtro jerárquico por país (ej. ARG, URY, CHL)",
    )
    sector: Optional[str] = Field(
        default=None,
        description="Filtro por sector productivo o económico",
    )
    ocupacion: Optional[str] = Field(
        default=None,
        description="Filtro por ocupación de referencia",
    )
    desde: Optional[str] = Field(
        default=None,
        description="Límite temporal inicial del rango (ej. 2023, 2024-Q1)",
    )
    hasta: Optional[str] = Field(
        default=None,
        description="Límite temporal final del rango (ej. 2024, 2024-Q4)",
    )

    @field_validator("*", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """Convierte cadenas en blanco o vacías a None para sanitización uniforme."""
        if isinstance(value, str) and not value.strip():
            return None
        return value


class IndicadorItemSchema(BaseModel):
    """Estructura de datos para un indicador individual del Observatorio.

    Attributes:
        pais: Código o nombre del país (ej. ARG, URY, CHL).
        sector: Sector económico o productivo (ej. Tecnología, Salud).
        ocupacion: Ocupación analizada si aplica.
        indicador: Clave o nombre del indicador (ej. tasa_desempleo).
        periodo: Período temporal del dato (ej. 2024-Q1, 2024).
        valor: Valor numérico del indicador.
        tipo: Tipo metodológico del dato (observado, calculado, proyeccion).
        fuente: Organismo o entidad proveedora del dato.
        fecha_actualizacion: Fecha de última actualización (YYYY-MM-DD).
    """

    model_config = ConfigDict(frozen=True)

    pais: str = Field(
        ...,
        description="Identificador o código del país (ej. ARG, URY, CHL)",
    )
    sector: Optional[str] = Field(
        default=None,
        description="Sector productivo o rama de actividad económica",
    )
    ocupacion: Optional[str] = Field(
        default=None,
        description="Ocupación de referencia según taxonomía normalizada",
    )
    indicador: str = Field(
        ...,
        description="Nombre o identificador clave del indicador",
    )
    periodo: str = Field(
        ...,
        description="Período temporal del indicador (ej. 2024-Q1)",
    )
    valor: float = Field(
        ...,
        description="Valor numérico registrado o proyectado",
    )
    tipo: str = Field(
        ...,
        description="Tipo metodológico: observado, calculado o proyeccion",
    )
    fuente: str = Field(
        ...,
        description="Fuente u organismo oficial de procedencia del dato",
    )
    fecha_actualizacion: str = Field(
        ...,
        description="Fecha de última actualización del indicador (YYYY-MM-DD)",
    )


# Envoltorio tipado de respuesta estándar para el listado de indicadores
IndicadoresResponseSchema = ApiResponse[List[IndicadorItemSchema]]
