from abc import ABC, abstractmethod

from app.domain.entities.brecha import HabilidadComparada


class IBrechaRepository(ABC):
    """Puerto abstracto para el repositorio de brechas de habilidades."""

    @abstractmethod
    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparada]:
        """Obtiene la lista de habilidades comparadas para una ocupacion dada."""
        pass

    @abstractmethod
    async def save_habilidades(
        self, ocupacion: str, habilidades: list[HabilidadComparada]
    ) -> list[HabilidadComparada]:
        """Persiste o actualiza un lote de habilidades comparadas
        para una ocupación dada.
        """
        pass

    @abstractmethod
    async def get_all_ocupaciones(self) -> list[str]:
        """Obtiene el listado de ocupaciones que cuentan con brechas registradas."""
        pass
