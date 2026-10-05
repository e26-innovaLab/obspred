"""Contrato abstracto / interfaz para el repositorio de indicadores."""

from typing import Optional, Protocol

from app.domain.entities.study_indicator import StudyIndicator


class StudyIndicatorRepositoryInterface(Protocol):
    """Protocolo que desacopla la lógica de negocio de la base de datos física.

    Cualquier repositorio real (SQLAlchemy, MongoDB, Fake en memoria)
    debe implementar estos métodos.
    """

    async def get_by_id(self, indicator_id: str) -> Optional[StudyIndicator]:
        """Obtiene un indicador por su identificador único.

        Args:
            indicator_id: ID del indicador buscado.

        Returns:
            Optional[StudyIndicator]: Instancia encontrada o None.
        """
        ...

    async def list_all(
        self,
        country: Optional[str] = None,
        sector: Optional[str] = None,
    ) -> list[StudyIndicator]:
        """Lista indicadores aplicando filtros opcionales de país y sector.

        Args:
            country: Código de país para filtrar.
            sector: Nombre del sector para filtrar.

        Returns:
            list[StudyIndicator]: Lista de indicadores coincidentes.
        """
        ...

    async def save(self, indicator: StudyIndicator) -> StudyIndicator:
        """Persiste o actualiza un indicador.

        Args:
            indicator: Entidad de dominio a persistir.

        Returns:
            StudyIndicator: Entidad persistida.
        """
        ...
