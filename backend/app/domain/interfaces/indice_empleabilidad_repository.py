"""Contrato abstracto del repositorio para el Índice de Empleabilidad."""

from abc import ABC, abstractmethod

from app.domain.entities.indice_empleabilidad import IndiceEmpleabilidad


class IIndiceEmpleabilidadRepository(ABC):
    """Puerto abstracto para la consulta y cálculo del Índice de Empleabilidad."""

    @abstractmethod
    async def get_by_ocupacion(
        self,
        ocupacion: str,
        pais: str | None = None,
        sector: str | None = None,
        periodo: str | None = None,
    ) -> IndiceEmpleabilidad | None:
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

    @abstractmethod
    async def get_ranking(
        self,
        paises: list[str],
        sector: str | None = None,
        periodo: str | None = None,
    ) -> list[IndiceEmpleabilidad]:
        """Obtiene el listado clasificado de ocupaciones para ranking multi-país.

        Args:
            paises: Lista de códigos ISO-3 de países a incluir.
            sector: Filtro opcional por sector estratégico.
            periodo: Período temporal de referencia.

        Returns:
            list[IndiceEmpleabilidad]: Lista de entidades del índice con puestos
                disponibles y scores calculados por país y ocupación.
        """
        pass
