"""Entidades y objetos de valor del dominio para Series Temporales Históricas."""

import math
from dataclasses import dataclass, field
from datetime import date

from app.core.constants import TipoIndicador


@dataclass(frozen=True)
class PuntoSerieTemporal:
    """Punto temporal individual de una serie de tiempo.

    Attributes:
        periodo: Etiqueta o fecha del período (ej. '2024', '2024-03', '2024-Q1').
        valor: Valor numérico observado o calculado para el período.
        tipo: Clasificación metodológica del dato (por defecto 'observado').
        fuente: Organismo oficial proveedor del dato (ej. 'Banco Central de Chile').
        fecha_actualizacion: Fecha en que se sincronizó o registró el dato.
    """

    periodo: str
    valor: float
    tipo: str = TipoIndicador.OBSERVADO
    fuente: str = ""
    fecha_actualizacion: date | None = None

    def __post_init__(self) -> None:
        """Valida invariantes del punto temporal tras inicializarse.

        Raises:
            ValueError: Si el período está vacío o el valor no es un número finito.
        """
        if not self.periodo or not self.periodo.strip():
            raise ValueError("El período temporal no puede estar vacío.")
        if math.isnan(self.valor) or math.isinf(self.valor):
            raise ValueError(
                f"El valor de la observación en '{self.periodo}' "
                "debe ser un número finito válido."
            )


@dataclass(frozen=True)
class SerieHistorica:
    """Entidad principal que representa una serie histórica de un indicador.

    Attributes:
        pais: Código ISO3 normalizado del país (ej. 'CHL', 'ARG', 'URY').
        indicador: Identificador estándar del indicador (ej. 'tasa_desempleo').
        observaciones: Lista cronológica de observaciones que componen la serie.
        sector: Sector económico específico si aplica (None para agregado nacional).
        ocupacion: Ocupación laboral específica si aplica.
        periodo_desde: Período inicial del filtro temporal consultado.
        periodo_hasta: Período final del filtro temporal consultado.
    """

    pais: str
    indicador: str
    observaciones: list[PuntoSerieTemporal] = field(default_factory=list)
    sector: str | None = None
    ocupacion: str | None = None
    periodo_desde: str | None = None
    periodo_hasta: str | None = None

    def __post_init__(self) -> None:
        """Valida invariantes de la serie histórica tras su inicialización.

        Raises:
            ValueError: Si el país, indicador o rango temporal son inconsistentes.
        """
        if not self.pais or not self.pais.strip():
            raise ValueError("El código de país no puede estar vacío.")
        if len(self.pais.strip()) != 3:
            msg_pais = (
                f"El código de país '{self.pais}' debe tener "
                "exactamente 3 caracteres (ISO3)."
            )
            raise ValueError(msg_pais)
        if not self.indicador or not self.indicador.strip():
            raise ValueError("El nombre del indicador no puede estar vacío.")
        if (
            self.periodo_desde
            and self.periodo_hasta
            and self.periodo_desde > self.periodo_hasta
        ):
            msg_periodo = (
                f"El período inicial '{self.periodo_desde}' no puede ser "
                f"posterior al final '{self.periodo_hasta}'."
            )
            raise ValueError(msg_periodo)

    @property
    def total_observaciones(self) -> int:
        """Retorna la cantidad total de observaciones en la serie."""
        return len(self.observaciones)

    @property
    def fuentes_involucradas(self) -> list[str]:
        """Obtiene el listado único y ordenado de fuentes de la serie."""
        return sorted({obs.fuente for obs in self.observaciones if obs.fuente})
