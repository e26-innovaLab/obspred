"""Implementación SQLAlchemy para el repositorio de series históricas."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.serie_historica import PuntoSerieTemporal
from app.domain.interfaces.serie_historica_repository import (
    ISerieHistoricaRepository,
)
from app.infrastructure.persistence.models import IndicadorModel


class SqlAlchemySerieHistoricaRepository(ISerieHistoricaRepository):
    """Adaptador de persistencia para consultar series temporales en DB."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_serie_temporal(
        self,
        pais: str,
        indicador: str,
        sector: str | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[PuntoSerieTemporal]:
        """Consulta observaciones históricas ordenadas cronológicamente."""
        filtros = [
            IndicadorModel.pais == pais,
            IndicadorModel.indicador == indicador,
        ]

        if sector is not None:
            filtros.append(IndicadorModel.sector == sector)

        if periodo_desde is not None:
            filtros.append(IndicadorModel.periodo >= periodo_desde)

        if periodo_hasta is not None:
            filtros.append(IndicadorModel.periodo <= periodo_hasta)

        query = (
            select(IndicadorModel)
            .where(and_(*filtros))
            .order_by(IndicadorModel.periodo.asc())
        )

        result = await self._session.execute(query)
        filas = result.scalars().all()

        return [
            PuntoSerieTemporal(
                periodo=f.periodo,
                valor=float(f.valor),
                tipo=f.tipo,
                fuente=f.fuente,
            )
            for f in filas
        ]

    # Alias por si el servicio llama a get_serie_historica
    async def get_serie_historica(
        self,
        pais: str,
        indicador: str,
        sector: str | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[PuntoSerieTemporal]:
        return await self.get_serie_temporal(
            pais=pais,
            indicador=indicador,
            sector=sector,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    async def get_ultimo_indicador(
        self,
        pais: str,
        indicador: str,
        sector: str | None = None,
    ) -> PuntoSerieTemporal | None:
        """Consulta el último registro cronológico para un indicador dado."""
        filtros = [
            IndicadorModel.pais == pais,
            IndicadorModel.indicador == indicador,
        ]

        if sector is not None:
            filtros.append(IndicadorModel.sector == sector)

        query = (
            select(IndicadorModel)
            .where(and_(*filtros))
            .order_by(IndicadorModel.periodo.desc())
            .limit(1)
        )

        result = await self._session.execute(query)
        fila = result.scalars().first()

        if fila is None:
            return None

        return PuntoSerieTemporal(
            periodo=fila.periodo,
            valor=float(fila.valor),
            tipo=fila.tipo,
            fuente=fila.fuente,
        )
