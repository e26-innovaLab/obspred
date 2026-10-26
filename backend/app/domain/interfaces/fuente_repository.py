from abc import ABC, abstractmethod

from app.core.constants import FuenteEstado
from app.domain.entities.fuente import Fuente
from typing import Optional


class IFuenteRepository(ABC):
    """Puerto abstracto para operaciones de persistencia y consulta de fuentes de datos."""

    @abstractmethod
    async def get_by_estado(self, estado: FuenteEstado) -> list[Fuente]:
        """Consulta las fuentes de datos filtrando por su estado.

        Args:
            estado (FuenteEstado): Estado de la fuente a filtrar.

        Returns:
            List[FuenteModel]: Lista de modelos ORM coincidentes con el estado.
        """
        pass

    @abstractmethod
    async def get_by_id(self, fuente_id: int) -> Fuente | None:
        """Consulta una fuente de datos por su ID.

        Args:
            fuente_id (int): ID de la fuente a consultar.

        Returns:
            fuente: Modelo ORM de la fuente si existe, None si no.
        """
        pass
    
    @abstractmethod
    async def save(self, fuente: Fuente) -> None:
        """Guarda una nueva fuente de datos en la base de datos.

        Args:
            fuente (Fuente): Instancia de la fuente a guardar.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[Fuente]:
        """Consulta todas las fuentes de datos disponibles.

        Returns:
            List[Fuente]: Lista de todas las fuentes de datos.
        """
        pass