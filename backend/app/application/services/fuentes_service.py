from app.application.dtos.fuentes_dto import FuenteDTO
from app.core.constants import FuenteEstado
from app.domain.entities.fuente import Fuente
from app.domain.interfaces.fuente_repository import IFuenteRepository


class FuenteService:
    """Servicio de aplicación para la gestión de fuentes de datos."""

    def __init__(self, fuente_repository: IFuenteRepository):
        """Inicializa el servicio con un repositorio de fuentes.

        Args:
            fuente_repository (IFuenteRepository): Repositorio para la persistencia
            y para consultar  fuentes.

        """
        self.fuente_repository = fuente_repository

    @staticmethod
    def _map_entity_to_dto(fuente: Fuente) -> FuenteDTO:
        """Convierte una entidad Fuente a un DTO FuenteDTO.

        Args:
            fuente (Fuente): Entidad de dominio Fuente.

        Returns:
            FuenteDTO: DTO correspondiente a la entidad.
        """
        return FuenteDTO(
            id=fuente.id,
            nombre=fuente.nombre,
            descripcion=fuente.descripcion,
            estado=fuente.estado,
            url=fuente.url,
            ultima_actualizacion=fuente.ulima_actualizacion,
        )

    async def get_fuentes_by_estado(self, estado: FuenteEstado) -> list[FuenteDTO]:
        """Obtiene las fuentes de datos filtrando por su estado.

        Args:
            estado (FuenteEstado): Estado de la fuente a filtrar.

        Returns:
            List[Fuente]: Lista de entidades Fuente coincidentes con el estado.
        """
        fuentes = await self.fuente_repository.get_by_estado(estado)
        return [self._map_entity_to_dto(fuente) for fuente in fuentes]

    async def get_fuente_by_id(self, fuente_id: int) -> FuenteDTO | None:
        """Obtiene una fuente de datos por su ID.

        Args:
            fuente_id (int): ID de la fuente a consultar.

        Returns:
            Fuente | None: Entidad Fuente si existe, None si no.
        """
        fuente = await self.fuente_repository.get_by_id(fuente_id)
        if fuente is None:
            return None
        return self._map_entity_to_dto(fuente)

    async def create_fuente(self, fuente_dto: FuenteDTO) -> None:
        """Guarda una nueva fuente de datos en la base de datos.

        Args:
            fuente_dto (FuenteDTO): DTO de la fuente a guardar.
        """
        fuente = Fuente(
            nombre=fuente_dto.nombre,
            descripcion=fuente_dto.descripcion,
            url=fuente_dto.url,
            ulima_actualizacion=fuente_dto.ultima_actualizacion,
        )
        await self.fuente_repository.save(fuente)

    async def get_all_fuentes(self) -> list[FuenteDTO]:
        """Obtiene todas las fuentes de datos disponibles.

        Returns:
            List[Fuente]: Lista de todas las fuentes de datos.
        """
        fuentes = await self.fuente_repository.get_all()
        return [self._map_entity_to_dto(fuente) for fuente in fuentes]
