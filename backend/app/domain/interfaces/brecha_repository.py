from abc import ABC, abstractmethod

from app.domain.entities.brecha import HabilidadComparada


class IBrechaRepository(ABC):
    """Puerto abstracto para el repositorio de brechas de habilidades."""

    @abstractmethod
    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparada]:
        """Obtiene la lista de habilidades comparadas para una ocupacion dada."""
        pass
