"""Esquemas Pydantic para la consulta y serialización del Índice de Empleabilidad."""

from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.schemas.response_schema import ApiResponse


class IndiceEmpleabilidadFilterSchema(BaseModel):
    """Parámetros de consulta y filtrado para el Índice de Empleabilidad.

    Normaliza y sanitiza automáticamente los filtros entrantes desde Query parameters,
    transformando cadenas vacías o compuestas únicamente por espacios en None.

    Attributes:
        pais: Filtro opcional por país (ej. ARG, URY, CHL).
        sector: Filtro opcional por sector productivo o económico.
        periodo: Período temporal de análisis (ej. 2026-Q1).
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
        description="Filtro por sector productivo o estratégico",
    )
    periodo: Optional[str] = Field(
        default=None,
        description="Período temporal analizado (ej. 2026-Q1)",
    )

    @field_validator("*", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """Convierte cadenas vacías o espacios en blanco a None para sanitización."""
        if isinstance(value, str) and not value.strip():
            return None
        return value


class DimensionIndiceSchema(BaseModel):
    """Esquema de serialización para una dimensión del Índice de Empleabilidad.

    Attributes:
        nombre: Nombre de la dimensión analítica.
        valor: Puntuación normalizada en escala de 0.0 a 100.0.
        peso: Ponderación o ponderador de la dimensión (0.0 a 1.0).
        descripcion: Resumen explicativo o detalle de la dimensión.
    """

    model_config = ConfigDict(frozen=True)

    nombre: str = Field(
        ...,
        description="Denominación de la dimensión analítica",
        examples=["Demanda de puestos"],
    )
    valor: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Puntuación normalizada en escala de 0.0 a 100.0",
        examples=[88.0],
    )
    peso: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ponderación asignada a la dimensión (0.0 a 1.0)",
        examples=[0.35],
    )
    descripcion: Optional[str] = Field(
        default=None,
        description="Explicación contextual de la dimensión",
    )


class EvolucionIndicePuntoSchema(BaseModel):
    """Esquema para un punto histórico en la evolución del índice.

    Attributes:
        periodo: Período temporal del dato (ej. 2025-Q3).
        valor: Puntuación del índice en dicho período (0.0 a 100.0).
    """

    model_config = ConfigDict(frozen=True)

    periodo: str = Field(
        ...,
        description="Período temporal de la observación (ej. 2025-Q3)",
    )
    valor: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Puntuación del índice en el período (0.0 a 100.0)",
    )


class IndiceEmpleabilidadDataSchema(BaseModel):
    """Estructura de datos para el Índice de Empleabilidad de una ocupación.

    Attributes:
        ocupacion_id: Identificador estandarizado de la ocupación (ej. dev-software).
        ocupacion_nombre: Nombre canónico de la ocupación.
        score: Score general agregado del índice (0.0 a 100.0).
        nivel: Clasificación cualitativa (Muy Alto, Alto, Medio, Bajo).
        dimensiones: Desglose de dimensiones componentes con sus ponderaciones.
        tipo: Tipo metodológico del indicador (siempre 'calculado').
        fuente: Fuente u organismos oficiales proveedores del dato.
        fecha_actualizacion: Fecha de última actualización (YYYY-MM-DD).
        metodologia: Detalle metodológico del cálculo.
        pais: País de referencia si fue filtrado.
        sector: Sector estratégico asociado.
        periodo: Período temporal de referencia.
        evolucion: Serie temporal histórica de puntos del índice.
    """

    model_config = ConfigDict(frozen=True)

    ocupacion_id: str = Field(
        ...,
        description="Identificador normalizado de la ocupación",
        examples=["dev-software"],
    )
    ocupacion_nombre: str = Field(
        ...,
        description="Nombre canónico de la ocupación",
        examples=["Desarrollador/a de software"],
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Score global agregado del Índice de Empleabilidad (0 a 100)",
        examples=[81.3],
    )
    nivel: str = Field(
        ...,
        description="Nivel cualitativo: Muy Alto, Alto, Medio o Bajo",
        examples=["Muy Alto"],
    )
    dimensiones: List[DimensionIndiceSchema] = Field(
        ...,
        description="Desglose de dimensiones componentes con sus pesos",
    )
    tipo: str = Field(
        default="calculado",
        description="Tipo metodológico del indicador (calculado)",
    )
    fuente: str = Field(
        ...,
        description="Fuente u organismos oficiales de procedencia de los datos",
    )
    fecha_actualizacion: date = Field(
        ...,
        description="Fecha de última actualización o corte (YYYY-MM-DD)",
    )
    metodologia: str = Field(
        ...,
        description="Descripción metodológica del algoritmo y ponderaciones",
    )
    pais: Optional[str] = Field(
        default=None,
        description="País de análisis si fue filtrado",
    )
    sector: Optional[str] = Field(
        default=None,
        description="Sector estratégico asociado",
    )
    periodo: Optional[str] = Field(
        default=None,
        description="Período de referencia temporal",
    )
    evolucion: List[EvolucionIndicePuntoSchema] = Field(
        default_factory=list,
        description="Serie temporal de evolución histórica del índice",
    )


# Envoltorio tipado de respuesta estándar para el endpoint
IndiceEmpleabilidadResponseSchema = ApiResponse[IndiceEmpleabilidadDataSchema]
