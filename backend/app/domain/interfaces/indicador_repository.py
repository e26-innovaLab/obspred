"""Contrato abstracto del repositorio de persistencia para Indicadores."""

from abc import ABC, abstractmethod

from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.infrastructure.persistence.models.indicador import IndicadorModel


class IIndicadorRepository(ABC):
    """Puerto abstracto para operaciones de persistencia y consulta de indicadores."""

    @abstractmethod
    async def upsert_batch(self, records: list[RawIndicatorRecord]) -> int:
        """Inserta o actualiza un lote de registros de indicadores de forma idempotente.

        Args:
            records: Lista de registros normalizados a almacenar o actualizar.

        Returns:
            int: Cantidad de registros efectivamente procesados y persistidos.
        """
        pass

    @abstractmethod
    async def get_by_filters(
        self,
        pais: str | None = None,
        sector: str | None = None,
        ocupacion: str | None = None,
        indicador: str | None = None,
        desde: str | None = None,
        hasta: str | None = None,
    ) -> list[IndicadorModel]:
        """Consulta registros de indicadores aplicando la jerarquía estricta de filtros.

        Args:
            pais: Código opcional del país (ej. ARG, URY, CHL).
            sector: Sector económico opcional de filtrado.
            ocupacion: Ocupación opcional de filtrado.
            indicador: Identificador clave del indicador.
            desde: Período temporal inicial del rango.
            hasta: Período temporal final del rango.

        Returns:
            List[IndicadorModel]: Lista de modelos ORM coincidentes con los filtros.
        """
        pass
