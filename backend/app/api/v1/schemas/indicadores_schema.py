"""Esquemas Pydantic para la consulta y serialización de indicadores."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse


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
