"""Contrato abstracto del repositorio para Series Temporales Históricas."""

from abc import ABC, abstractmethod

from app.domain.entities.serie_historica import PuntoSerieTemporal


class ISerieHistoricaRepository(ABC):
    """Puerto abstracto para la consulta y recuperación de series temporales."""

    @abstractmethod
    async def get_serie_temporal(
        self,
        pais: str,
        indicador: str,
        sector: str | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[PuntoSerieTemporal]:
        """Obtiene la serie cronológica de observaciones para un país e indicador.

        Args:
            pais: Código ISO3 del país (ej. ARG, URY, CHL).
            indicador: Identificador estándar (ej. tasa_desempleo, tasa_empleo).
            sector: Sector económico opcional de filtrado (None para agregado nacional).
            periodo_desde: Período inicial opcional (ej. 2024 o 2024-Q1).
            periodo_hasta: Período final opcional (ej. 2026 o 2026-Q4).

        Returns:
            list[PuntoSerieTemporal]: Observaciones ordenadas
            cronológicamente de forma ascendente.
        """
        pass

    @abstractmethod
    async def get_ultimo_indicador(
        self,
        pais: str,
        indicador: str,
        sector: str | None = None,
    ) -> PuntoSerieTemporal | None:
        """Obtiene la observación más reciente para alimentar tarjetas resumen.

        Args:
            pais: Código ISO3 del país.
            indicador: Identificador estándar del indicador.
            sector: Sector económico opcional.

        Returns:
            PuntoSerieTemporal | None: El punto más reciente o None si no hay datos.
        """
        pass
