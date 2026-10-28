from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.brecha import HabilidadComparada
from app.domain.interfaces.brecha_repository import IBrechaRepository
from app.infrastructure.persistence.models.brecha_model import HabilidadBrechaModel


def _normalize_ocupacion(val: str) -> str:
    """Normaliza identificadores de ocupación reemplazando guiones y espacios."""
    return val.strip().lower().replace("-", "_").replace(" ", "_")


class SQLAlchemyBrechaRepository(IBrechaRepository):
    """Implementación concreta del repositorio de brechas usando SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa el repositorio con la sesión transaccional de SQLAlchemy.

        Args:
            db: Sesión asíncrona de base de datos.
        """
        self.db = db

    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparada]:
        """Obtiene la lista de habilidades comparadas para una ocupación.

        Args:
            ocupacion: Identificador o nombre normalizado de la ocupación.

        Returns:
            list[HabilidadComparada]: Entidades de dominio encontradas.
        """
        norm = _normalize_ocupacion(ocupacion)
        # Búsqueda directa o normalizada sobre la columna ocupacion
        stmt = select(HabilidadBrechaModel).where(
            func.lower(
                func.replace(
                    func.replace(HabilidadBrechaModel.ocupacion, "-", "_"), " ", "_"
                )
            )
            == norm
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

    async def save_habilidades(
        self, ocupacion: str, habilidades: list[HabilidadComparada]
    ) -> list[HabilidadComparada]:
        """Persiste o actualiza un lote de habilidades comparadas para una ocupación.

        Args:
            ocupacion: Nombre o identificador canónico de la ocupación.
            habilidades: Lista de entidades de dominio a guardar.

        Returns:
            list[HabilidadComparada]: Entidades de dominio tras la persistencia.
        """
        norm_ocupacion = _normalize_ocupacion(ocupacion)

        for h in habilidades:
            # Upsert idempotente por (ocupacion, habilidad)
            stmt = select(HabilidadBrechaModel).where(
                func.lower(
                    func.replace(
                        func.replace(HabilidadBrechaModel.ocupacion, "-", "_"), " ", "_"
                    )
                )
                == norm_ocupacion,
                func.lower(HabilidadBrechaModel.habilidad)
                == h.habilidad.strip().lower(),
            )
            res = await self.db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.demanda = h.demanda
                existing.oferta_formativa = h.oferta_formativa
                existing.emergente = h.emergente
            else:
                new_model = HabilidadBrechaModel(
                    ocupacion=norm_ocupacion,
                    habilidad=h.habilidad.strip(),
                    demanda=h.demanda,
                    oferta_formativa=h.oferta_formativa,
                    emergente=h.emergente,
                )
                self.db.add(new_model)

        await self.db.commit()
        return await self.get_by_ocupation(norm_ocupacion)

    async def get_all_ocupaciones(self) -> list[str]:
        """Obtiene la lista de ocupaciones distintas que tienen datos persistidos.

        Returns:
            list[str]: Ocupaciones disponibles.
        """
        stmt = select(HabilidadBrechaModel.ocupacion).distinct()
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
