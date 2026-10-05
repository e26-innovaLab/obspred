"""Repositorio simulado en memoria para indicadores de estudio."""

from typing import Optional

from app.domain.entities.study_indicator import StudyIndicator
from app.domain.interfaces.study_indicator_repository import (
    StudyIndicatorRepositoryInterface,
)


class FakeStudyIndicatorRepository(StudyIndicatorRepositoryInterface):
    """Implementación en memoria de StudyIndicatorRepositoryInterface.

    Sirve para fines educativos y desarrollo sin requerir una base de datos activa.
    """

    def __init__(self) -> None:
        """Inicializa el repositorio con indicadores representativos de la región."""
        self._indicators: dict[str, StudyIndicator] = {
            "ind-ar-01": StudyIndicator(
                id="ind-ar-01",
                name="Tasa de Desempleo Abierto",
                country="AR",
                sector="Tecnología",
                value=7.6,
                unit="%",
                source="INDEC - EPH",
            ),
            "ind-cl-01": StudyIndicator(
                id="ind-cl-01",
                name="Demanda de Desarrolladores de Software",
                country="CL",
                sector="Tecnología",
                value=84.2,
                unit="Score Demanda",
                source="SENCE - SABE Chile",
            ),
            "ind-uy-01": StudyIndicator(
                id="ind-uy-01",
                name="Ocupación en Servicios Globales y TI",
                country="UY",
                sector="Tecnología",
                value=12500.0,
                unit="Puestos Registrados",
                source="INE Uruguay - ECH",
            ),
            "ind-ar-02": StudyIndicator(
                id="ind-ar-02",
                name="Remuneración Real Promedio en Salud",
                country="AR",
                sector="Salud",
                value=1150.0,
                unit="USD PPA",
                source="Secretaría de Trabajo AR",
            ),
        }

    async def get_by_id(self, indicator_id: str) -> Optional[StudyIndicator]:
        """Recupera un indicador por ID de la memoria."""
        return self._indicators.get(indicator_id)

    async def list_all(
        self,
        country: Optional[str] = None,
        sector: Optional[str] = None,
    ) -> list[StudyIndicator]:
        """Filtra los indicadores en memoria."""
        results = list(self._indicators.values())

        if country:
            results = [item for item in results if item.country == country]

        if sector:
            results = [
                item for item in results if item.sector.lower() == sector.lower()
            ]

        return results

    async def save(self, indicator: StudyIndicator) -> StudyIndicator:
        """Almacena el indicador en el diccionario interno."""
        self._indicators[indicator.id] = indicator
        return indicator
