from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.brecha import HabilidadComparada
from app.domain.interfaces.brecha_repository import IBrechaRepository
from app.infrastructure.persistence.models.brecha_model import HabilidadBrechaModel


class SQLAlchemyBrechaRepository(IBrechaRepository):
    """Implementación concreta del repositorio de brechas usando SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparada]:
        stmt = select(HabilidadBrechaModel).where(
            HabilidadBrechaModel.ocupacion == ocupacion
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()

        return [
            HabilidadComparada(
                habilidad=row.habilidad,
                demanda=row.demanda,
                oferta_formativa=row.oferta_formativa,
                emergente=row.emergente,
            )
            for row in rows
        ]
