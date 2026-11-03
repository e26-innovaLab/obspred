"""Implementación SQLAlchemy para el repositorio de persistencia de Indicadores."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.domain.interfaces.indicador_repository import IIndicadorRepository
from app.infrastructure.persistence.models.indicador import IndicadorModel


class SqlAlchemyIndicadorRepository(IIndicadorRepository):
    """Repositorio asíncrono para almacenamiento y consulta de series de indicadores."""

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con la sesión transaccional inyectada.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        self._session = session

    async def upsert_batch(self, records: list[RawIndicatorRecord]) -> int:
        """Inserta o actualiza indicadores respetando unicidad de clave lógica.

        La clave lógica de unicidad se compone de:
        (pais, sector, ocupacion, indicador, periodo, trimestre, fuente).

        Args:
            records: Lista de registros inmutables a persistir.

        Returns:
            int: Cantidad de registros procesados exitosamente.
        """
        if not records:
            return 0

        # Deduplicar en memoria preservando el último registro para cada clave lógica
        deduped_records: dict[tuple, RawIndicatorRecord] = {}
        for r in records:
            key = (
                r.pais,
                r.sector,
                r.ocupacion,
                r.indicador,
                r.periodo,
                r.trimestre,
                r.fuente,
            )
            deduped_records[key] = r

        unique_records = list(deduped_records.values())
        persisted_count = 0
        now_utc = datetime.now(UTC)

        for record in unique_records:
            # Búsqueda de registro existente bajo clave lógica completa
            query = select(IndicadorModel).where(
                IndicadorModel.pais == record.pais,
                IndicadorModel.indicador == record.indicador,
                IndicadorModel.periodo == record.periodo,
                IndicadorModel.fuente == record.fuente,
            )

            # Manejo explícito de nulos para sector y ocupación
            if record.sector is not None:
                query = query.where(IndicadorModel.sector == record.sector)
            else:
                query = query.where(IndicadorModel.sector.is_(None))

            if record.ocupacion is not None:
                query = query.where(IndicadorModel.ocupacion == record.ocupacion)
            else:
                query = query.where(IndicadorModel.ocupacion.is_(None))

            # Manejo explícito de nulos para trimestre
            if record.trimestre is not None:
                query = query.where(IndicadorModel.trimestre == record.trimestre)
            else:
                query = query.where(IndicadorModel.trimestre.is_(None))

            result = await self._session.execute(query)
            existing = result.scalars().first()

            if existing:
                existing.valor = record.valor
                existing.tipo = record.tipo
                existing.trimestre = record.trimestre
                existing.fecha_actualizacion = record.fecha_actualizacion
                existing.updated_at = now_utc
            else:
                new_model = IndicadorModel(
                    pais=record.pais,
                    sector=record.sector,
                    ocupacion=record.ocupacion,
                    indicador=record.indicador,
                    periodo=record.periodo,
                    trimestre=record.trimestre,
                    valor=record.valor,
                    tipo=record.tipo,
                    fuente=record.fuente,
                    fecha_actualizacion=record.fecha_actualizacion,
                    created_at=now_utc,
                )
                self._session.add(new_model)

            persisted_count += 1

        await self._session.commit()
        logger.info(
            "Persistencia en lote: %d registros procesados en 'indicadores'.",
            persisted_count,
        )
        return persisted_count

    async def get_by_filters(
        self,
        pais: str | None = None,
        sector: str | None = None,
        ocupacion: str | None = None,
        indicador: str | None = None,
        desde: str | None = None,
        hasta: str | None = None,
        trimestre: str | None = None,
    ) -> list[IndicadorModel]:
        """Consulta indicadores aplicando la jerarquía estricta de filtros.

        Args:
            pais: Código opcional del país.
            sector: Sector económico opcional.
            ocupacion: Ocupación opcional.
            indicador: Identificador clave del indicador.
            desde: Límite temporal inicial del rango.
            hasta: Límite temporal final del rango.
            trimestre: Filtro opcional por trimestre (ej. Q1, Q2, Q3, Q4).

        Returns:
            List[IndicadorModel]: Modelos ORM coincidentes ordenados cronológicamente.
        """
        stmt = select(IndicadorModel)

        if pais:
            stmt = stmt.where(IndicadorModel.pais == pais.upper().strip())
        if sector:
            stmt = stmt.where(IndicadorModel.sector == sector.strip())
        if ocupacion:
            stmt = stmt.where(IndicadorModel.ocupacion == ocupacion.strip())
        if indicador:
            stmt = stmt.where(IndicadorModel.indicador == indicador.strip())
        if desde:
            stmt = stmt.where(IndicadorModel.periodo >= desde.strip())
        if hasta:
            stmt = stmt.where(IndicadorModel.periodo <= hasta.strip())
        if trimestre:
            stmt = stmt.where(IndicadorModel.trimestre == trimestre.upper().strip())

        stmt = stmt.order_by(
            IndicadorModel.periodo.asc(),
            IndicadorModel.trimestre.asc().nulls_first(),
            IndicadorModel.pais.asc(),
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())
