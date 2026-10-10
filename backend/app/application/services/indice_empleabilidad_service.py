"""Servicio de aplicación para coordinar la consulta del Índice de Empleabilidad."""

from typing import Optional

from app.application.dtos.indice_empleabilidad_dto import (
    DimensionIndiceDTO,
    EvolucionIndicePuntoDTO,
    IndiceEmpleabilidadDTO,
)
from app.domain.exceptions.base import EntityNotFoundException
from app.domain.exceptions.indice_empleabilidad import InvalidOccupationException
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)


class IndiceEmpleabilidadService:
    """Servicio de aplicación que orquesta la obtención del Índice de Empleabilidad."""

    def __init__(self, repository: IIndiceEmpleabilidadRepository) -> None:
        """Inicializa el servicio inyectando el repositorio del índice.

        Args:
            repository: Puerto abstracto para acceder a datos del índice.
        """
        self._repository = repository

    async def get_indice_por_ocupacion(
        self,
        ocupacion: str,
        pais: Optional[str] = None,
        sector: Optional[str] = None,
        periodo: Optional[str] = None,
    ) -> IndiceEmpleabilidadDTO:
        """Consulta el Índice de Empleabilidad para una ocupación y filtros dados.

        Args:
            ocupacion: Identificador o nombre de la ocupación requerida.
            pais: Filtro opcional por código de país (ej. ARG, URY, CHL).
            sector: Filtro opcional por sector estratégico.
            periodo: Filtro opcional por período temporal.

        Returns:
            IndiceEmpleabilidadDTO: DTO con el índice y sus dimensiones.

        Raises:
            InvalidOccupationException: Si la ocupación está vacía o en blanco.
            EntityNotFoundException: Si la ocupación no existe en el catálogo o sistema.
        """
        sanitized_ocupacion = ocupacion.strip() if ocupacion else ""
        if not sanitized_ocupacion:
            raise InvalidOccupationException(
                "El identificador o nombre de ocupación no puede estar vacío."
            )

        sanitized_pais = pais.strip() if pais and pais.strip() else None
        sanitized_sector = sector.strip() if sector and sector.strip() else None
        sanitized_periodo = periodo.strip() if periodo and periodo.strip() else None

        entity = await self._repository.get_by_ocupacion(
            ocupacion=sanitized_ocupacion,
            pais=sanitized_pais,
            sector=sanitized_sector,
            periodo=sanitized_periodo,
        )

        if entity is None:
            raise EntityNotFoundException(
                entity_name="Occupation",
                entity_id=sanitized_ocupacion,
            )

        return IndiceEmpleabilidadDTO(
            ocupacion_id=entity.ocupacion_id,
            ocupacion_nombre=entity.ocupacion_nombre,
            score=entity.score,
            nivel=entity.nivel,
            dimensiones=[
                DimensionIndiceDTO(
                    nombre=d.nombre,
                    valor=d.valor,
                    peso=d.peso,
                    descripcion=d.descripcion,
                )
                for d in entity.dimensiones
            ],
            tipo=entity.tipo,
            fuente=entity.fuente,
            fecha_actualizacion=entity.fecha_actualizacion,
            metodologia=entity.metodologia,
            pais=entity.pais,
            sector=entity.sector,
            periodo=entity.periodo,
            evolucion=[
                EvolucionIndicePuntoDTO(
                    periodo=p.periodo,
                    valor=p.valor,
                )
                for p in entity.evolucion
            ],
        )
