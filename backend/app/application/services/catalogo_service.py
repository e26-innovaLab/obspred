"""Servicio de aplicación para coordinar consultas y seeding del catálogo maestro."""

import asyncio

from app.application.dtos.catalogo_dto import (
    CatalogoDataDTO,
    OcupacionCatalogoDTO,
)
from app.core.logging import logger
from app.domain.interfaces.catalogo_repository import ICatalogoRepository


class CatalogoService:
    """Caso de uso de consulta y gestión del catálogo de taxonomías del Observatorio."""

    def __init__(self, repository: ICatalogoRepository) -> None:
        self._repository = repository

    async def get_catalogo(self) -> CatalogoDataDTO:
        """Obtiene el catálogo completo consolidado para los filtros globales.

        Si las tablas maestras están vacías (ej. primer arranque en ambiente nuevo),
        ejecuta automáticamente una carga inicial idempotente de las taxonomías base.

        Returns:
            CatalogoDataDTO: DTO con países, sectores, ocupaciones, indicadores y rango.
        """
        paises = await self._repository.get_paises()

        # Auto-seeding si la base de datos no tiene cargadas las taxonomías maestras
        if not paises:
            logger.info(
                "Catálogo maestro vacío. Ejecutando carga inicial automática..."
            )
            await self._repository.seed_catalogo_inicial()
            paises = await self._repository.get_paises()

        # Consultas concurrentes para optimizar tiempo de respuesta
        sectores_task = self._repository.get_sectores()
        ocupaciones_task = self._repository.get_ocupaciones()
        indicadores_task = self._repository.get_indicadores()
        periodos_task = self._repository.get_rango_periodos()

        sectores, ocupaciones, indicadores, periodos = await asyncio.gather(
            sectores_task,
            ocupaciones_task,
            indicadores_task,
            periodos_task,
        )

        return CatalogoDataDTO(
            paises=paises,
            sectores=sectores,
            ocupaciones=ocupaciones,
            indicadores=indicadores,
            periodos=periodos,
        )

    async def get_ocupaciones_por_sector(
        self, sector_id: str
    ) -> list[OcupacionCatalogoDTO]:
        """Obtiene las ocupaciones pertenecientes a un sector específico."""
        return await self._repository.get_ocupaciones(sector_id=sector_id)

    async def seed_catalogo(self) -> dict[str, int]:
        """Ejecuta explícitamente la carga inicial idempotente del catálogo."""
        return await self._repository.seed_catalogo_inicial()
