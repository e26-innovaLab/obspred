"""Contratos abstractos para conectores de servicios externos y extracción de datos."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RawIndicatorRecord(BaseModel):
    """Representación normalizada en memoria de un registro de indicador extraído.

    Attributes:
        pais: Identificador ISO o código oficial del país (ej. ARG, URY, CHL).
        sector: Rama de actividad económica o sector según clasificación normalizada.
        ocupacion: Denominación o código normalizado de la ocupación analizada.
        indicador: Clave unificada del indicador (ej. tasa_desempleo).
        periodo: Cadena representativa del período temporal (ej. 2023, 2024-Q1).
        valor: Magnitud numérica observada o calculada.
        tipo: Tipo metodológico del dato (observado, calculado, proyeccion).
        fuente: Denominación oficial del organismo o servicio proveedor.
        fecha_actualizacion: Fecha de vigencia o publicación reportada por el origen.
        metadatos: Atributos contextuales complementarios reportados por la fuente.
    """

    model_config = ConfigDict(frozen=True)

    pais: str = Field(
        ...,
        description="Código normalizado del país (ej. ARG, URY, CHL)",
    )
    sector: Optional[str] = Field(
        default=None,
        description="Sector económico o productivo asociado",
    )
    ocupacion: Optional[str] = Field(
        default=None,
        description="Ocupación de referencia según taxonomía",
    )
    indicador: str = Field(
        ...,
        description="Identificador clave normalizado del indicador",
    )
    periodo: str = Field(
        ...,
        description="Período temporal del registro (ej. 2023, 2024-Q1)",
    )
    valor: float = Field(
        ...,
        description="Valor numérico extraído del origen oficial",
    )
    tipo: str = Field(
        default="observado",
        description="Tipo metodológico: observado, calculado o proyeccion",
    )
    fuente: str = Field(
        ...,
        description="Nombre del organismo o proveedor oficial",
    )
    fecha_actualizacion: date = Field(
        ...,
        description="Fecha de publicación o última actualización del dato",
    )
    metadatos: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadatos técnicos y contextuales de trazabilidad",
    )


class IExternalDataConnector(ABC):
    """Puerto abstracto para adaptadores de extracción de datos oficiales externos."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Denominación institucional de la fuente proveedora."""
        pass

    @abstractmethod
    async def fetch_indicators(
        self,
        paises: Optional[List[str]] = None,
        indicadores: Optional[List[str]] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
    ) -> List[RawIndicatorRecord]:
        """Extrae y transforma datos desde la API externa a registros normalizados.

        Args:
            paises: Lista opcional de códigos de países a consultar (ej. ['ARG']).
            indicadores: Lista opcional de indicadores específicos a extraer.
            periodo_desde: Límite temporal inferior (ej. '2020').
            periodo_hasta: Límite temporal superior (ej. '2024').

        Returns:
            List[RawIndicatorRecord]: Colección inmutable de registros normalizados.
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Verifica la conectividad y disponibilidad operativa del servicio remoto.

        Returns:
            bool: True si el endpoint remoto responde satisfactoriamente, False si no.
        """
        pass
