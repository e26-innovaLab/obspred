"""Contrato de interfaz para el repositorio de catálogo y taxonomías maestras."""

from abc import ABC, abstractmethod

from app.application.dtos.catalogo_dto import (
    IndicadorCatalogoDTO,
    OcupacionCatalogoDTO,
    PaisCatalogoDTO,
    PeriodosRangoDTO,
    SectorCatalogoDTO,
)


class ICatalogoRepository(ABC):
    """Interfaz abstracta para la persistencia y consulta del catálogo maestro."""

    @abstractmethod
    async def get_paises(self) -> list[PaisCatalogoDTO]:
        """Obtiene la lista de países activos ordenados según catálogo."""
        ...

    @abstractmethod
    async def get_sectores(self) -> list[SectorCatalogoDTO]:
        """Obtiene la lista de sectores estratégicos activos ordenados."""
        ...

    @abstractmethod
    async def get_ocupaciones(
        self, sector_id: str | None = None
    ) -> list[OcupacionCatalogoDTO]:
        """Obtiene las ocupaciones activas, opcionalmente filtradas por sector."""
        ...

    @abstractmethod
    async def get_indicadores(self) -> list[IndicadorCatalogoDTO]:
        """Obtiene las definiciones maestras de los indicadores disponibles."""
        ...

    @abstractmethod
    async def get_rango_periodos(self) -> PeriodosRangoDTO:
        """Calcula el rango cronológico real (min y max) de las observaciones."""
        ...

    @abstractmethod
    async def seed_catalogo_inicial(self) -> dict[str, int]:
        """Realiza la carga inicial idempotente de taxonomías maestras."""
        ...
