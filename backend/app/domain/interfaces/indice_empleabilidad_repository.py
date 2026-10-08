"""Contrato abstracto del repositorio para el Índice de Empleabilidad."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.indice_empleabilidad import IndiceEmpleabilidad


class IIndiceEmpleabilidadRepository(ABC):
    """Puerto abstracto para la consulta y cálculo del Índice de Empleabilidad."""

    @abstractmethod
    async def get_by_ocupacion(
        self,
        ocupacion: str,
        pais: Optional[str] = None,
        sector: Optional[str] = None,
        periodo: Optional[str] = None,
    ) -> Optional[IndiceEmpleabilidad]:
        """Obtiene el Índice de Empleabilidad calculado para una ocupación y filtros.

        Args:
            ocupacion: Identificador o nombre normalizado de la ocupación.
            pais: Código opcional del país (ej. ARG, URY, CHL).
            sector: Sector económico opcional de filtrado.
            periodo: Período temporal de referencia (ej. 2026-Q1).

        Returns:
            Optional[IndiceEmpleabilidad]: Entidad de dominio si la ocupación
                existe en el sistema o catálogo, o None en caso contrario.
        """
        pass

    @abstractmethod
    async def exists_ocupacion(self, ocupacion: str) -> bool:
        """Determina si la ocupación existe en el catálogo o base de datos.

        Args:
            ocupacion: Identificador o denominación de la ocupación.

        Returns:
            bool: True si la ocupación es válida y reconocida, False si no existe.
        """
        pass
