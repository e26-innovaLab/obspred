"""Servicio de aplicación para la gestión y cálculo de indicadores de estudio.

Este servicio ilustra las mejores prácticas para FastAPI:
1. No importa nada de FastAPI ni de HTTP (es completamente agnóstico al transporte).
2. Recibe sus dependencias por constructor mediante una abstracción (DIP).
3. Lanza excepciones de dominio cuando se violan reglas de negocio.
4. Es 100% testeable de forma unitaria sin base de datos ni servidor web.
"""

import uuid
from typing import Optional

from app.application.dtos.study_indicator_dto import (
    CreateStudyIndicatorDTO,
    StudyIndicatorFilterDTO,
)
from app.domain.entities.study_indicator import StudyIndicator
from app.domain.exceptions.base import DomainException, EntityNotFoundException
from app.domain.interfaces.study_indicator_repository import (
    StudyIndicatorRepositoryInterface,
)

# Países soportados según el alcance regional de obspred (AGENTS.md)
ALLOWED_COUNTRIES = {"AR", "CL", "UY"}


class StudyIndicatorService:
    """Servicio de aplicación que orquesta casos de uso sobre indicadores."""

    def __init__(self, repository: StudyIndicatorRepositoryInterface) -> None:
        """Inicializa el servicio inyectando el contrato del repositorio.

        Args:
            repository: Abstracción de acceso a datos para indicadores.
        """
        self._repository = repository

    async def get_indicator_by_id(self, indicator_id: str) -> StudyIndicator:
        """Obtiene un indicador por su identificador.

        Args:
            indicator_id: ID único del indicador.

        Returns:
            StudyIndicator: Entidad de dominio encontrada.

        Raises:
            EntityNotFoundException: Si el indicador no existe en el sistema.
        """
        indicator = await self._repository.get_by_id(indicator_id=indicator_id)
        if not indicator:
            # Buena práctica: Lanzar excepción de dominio, no HTTPException
            raise EntityNotFoundException(
                entity_name="StudyIndicator",
                entity_id=indicator_id,
            )
        return indicator

    async def list_indicators(
        self,
        filters: Optional[StudyIndicatorFilterDTO] = None,
    ) -> list[StudyIndicator]:
        """Consulta el catálogo de indicadores aplicando filtros de país y sector.

        Args:
            filters: Criterios opcionales de búsqueda.

        Returns:
            list[StudyIndicator]: Lista de indicadores filtrados.
        """
        country = filters.country.upper() if (filters and filters.country) else None
        sector = filters.sector if filters else None

        return await self._repository.list_all(country=country, sector=sector)

    async def create_indicator(self, dto: CreateStudyIndicatorDTO) -> StudyIndicator:
        """Valida y da de alta un nuevo indicador socioeconómico.

        Args:
            dto: Datos transferidos desde la capa de entrada.

        Returns:
            StudyIndicator: Entidad creada y persistida.

        Raises:
            DomainException: Si el país no está permitido o el valor es negativo.
        """
        country_code = dto.country.upper().strip()

        # Validación de regla de negocio 1: Alcance geográfico
        if country_code not in ALLOWED_COUNTRIES:
            raise DomainException(
                f"El país '{dto.country}' no está soportado. "
                f"Valores permitidos: {', '.join(sorted(ALLOWED_COUNTRIES))}."
            )

        # Validación de regla de negocio 2: Valores no negativos
        if dto.value < 0:
            raise DomainException(
                f"El valor del indicador no puede ser negativo (recibido: {dto.value})."
            )

        new_indicator = StudyIndicator(
            id=f"ind-{uuid.uuid4().hex[:8]}",
            name=dto.name.strip(),
            country=country_code,
            sector=dto.sector.strip(),
            value=dto.value,
            unit=dto.unit.strip(),
            source=dto.source.strip(),
        )

        return await self._repository.save(new_indicator)
