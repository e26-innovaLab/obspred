from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import FuenteEstado
from app.core.logging import logger
from app.domain.entities.fuente import Fuente
from app.domain.interfaces.fuente_repository import IFuenteRepository
from app.infrastructure.persistence.models.fuente import FuenteModel


class SqlAlchemyFuenteRepository(IFuenteRepository):
    """Repositorio para la gestión de fuentes de datos en la base de datos."""

    def __init__(self, session: AsyncSession):
        """Inicializa el repositorio con una sesión de base de datos asincrónica.

        Args:
            session (AsyncSession): Sesión de base de datos asincrónica.
        """
        self.session = session

    @staticmethod
    def _map_model_to_entity(fuente_model: FuenteModel) -> Fuente:
        """Convierte un modelo ORM de fuente a una entidad de dominio Fuente.

        Args:
            fuente_model (FuenteModel): Modelo ORM de la fuente.

        Returns:
            Fuente: Entidad de dominio correspondiente.
        """
        return Fuente(
            id=fuente_model.id,
            nombre=fuente_model.nombre,
            descripcion=fuente_model.descripcion,
            estado=fuente_model.estado,
            url=fuente_model.url,
            ulima_actualizacion=fuente_model.ultima_actualizacion,
        )

    async def get_by_estado(self, estado: FuenteEstado) -> list[Fuente]:
        """Consulta las fuentes de datos filtrando por su estado.

        Args:
            estado (FuenteEstado): Estado de la fuente a filtrar.

        Returns:
            List[Fuente]: Lista de entidades Fuente coincidentes con el estado.
        """
        query = select(FuenteModel).where(FuenteModel.estado == estado)
        result = await self.session.execute(query)
        fuentes_model = result.scalars().all()
        return [self._map_model_to_entity(fuente) for fuente in fuentes_model]

    async def get_by_id(self, fuente_id: int) -> Fuente | None:
        """Consulta una fuente de datos por su ID.

        Args:
            fuente_id (int): ID de la fuente a consultar.

        Returns:
            Optional[Fuente]: Entidad Fuente si existe, None si no.
        """
        query = select(FuenteModel).where(FuenteModel.id == fuente_id)
        result = await self.session.execute(query)
        fuente_model = result.scalar_one_or_none()
        if fuente_model:
            return self._map_model_to_entity(fuente_model)
        return None

    async def save(self, fuente: Fuente) -> None:
        """Guarda una nueva fuente de datos en la base de datos.

        Args:
            fuente (Fuente): Instancia de la fuente a guardar.
        """
        fuente_model = FuenteModel(
            nombre=fuente.nombre,
            descripcion=fuente.descripcion,
            estado=fuente.estado,
            url=fuente.url,
            ultima_actualizacion=fuente.ulima_actualizacion,
        )
        self.session.add(fuente_model)
        await self.session.commit()
        logger.info(f"Fuente '{fuente.nombre}' guardada con éxito.")

    async def get_all(self) -> list[Fuente]:
        """Consulta todas las fuentes de datos disponibles.

        Returns:
            List[Fuente]: Lista de todas las entidades Fuente.
        """
        query = select(FuenteModel)
        result = await self.session.execute(query)
        fuentes_model = result.scalars().all()
        return [self._map_model_to_entity(fuente) for fuente in fuentes_model]
