"""Pruebas unitarias para SQLAlchemyBrechaRepository."""

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.domain.entities.brecha import HabilidadComparada
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.repositories.brecha_repository import (
    SQLAlchemyBrechaRepository,
)


@pytest.fixture
async def in_memory_session() -> AsyncSession:
    """Provee una sesión SQLite en memoria con esquema creado para pruebas unitarias."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_brecha_repository_save_and_get(in_memory_session: AsyncSession) -> None:
    """Valida la persistencia en DB y la consulta de habilidades comparadas."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)

    habilidades = [
        HabilidadComparada(
            habilidad="Cloud computing",
            demanda=95.0,
            oferta_formativa=50.0,
            emergente=True,
        ),
        HabilidadComparada(
            habilidad="Python",
            demanda=80.0,
            oferta_formativa=90.0,
            emergente=False,
        ),
    ]

    saved = await repo.save_habilidades("desarrollador_software", habilidades)
    assert len(saved) == 2

    # Consulta por la ocupación persistida
    retrieved = await repo.get_by_ocupation("desarrollador_software")
    assert len(retrieved) == 2

    cloud = next(h for h in retrieved if h.habilidad == "Cloud computing")
    assert cloud.demanda == 95.0
    assert cloud.oferta_formativa == 50.0
    assert cloud.emergente is True
    assert cloud.brecha == 45.0  # 95 - 50

    python_skill = next(h for h in retrieved if h.habilidad == "Python")
    assert python_skill.brecha == 0.0  # max(0, 80 - 90)


@pytest.mark.asyncio
async def test_brecha_repository_idempotent_update(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que el guardado sucesivo actualice registros sin duplicar."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)

    inicial = [
        HabilidadComparada(
            habilidad="Data Analysis",
            demanda=80.0,
            oferta_formativa=40.0,
            emergente=False,
        )
    ]
    await repo.save_habilidades("analista_datos", inicial)

    # Actualizamos valores para la misma habilidad
    actualizado = [
        HabilidadComparada(
            habilidad="Data Analysis",
            demanda=90.0,
            oferta_formativa=45.0,
            emergente=True,
        )
    ]
    await repo.save_habilidades("analista_datos", actualizado)

    records = await repo.get_by_ocupation("analista_datos")
    assert len(records) == 1
    assert records[0].demanda == 90.0
    assert records[0].oferta_formativa == 45.0
    assert records[0].emergente is True
    assert records[0].brecha == 45.0


@pytest.mark.asyncio
async def test_brecha_repository_flexible_query(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que la consulta admita variantes de mayúsculas, guiones y espacios."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)

    await repo.save_habilidades(
        "desarrollador_software",
        [
            HabilidadComparada(
                habilidad="Git",
                demanda=70.0,
                oferta_formativa=60.0,
            )
        ],
    )

    # Consulta con guión y mayúsculas
    res_dash = await repo.get_by_ocupation("DESARROLLADOR-SOFTWARE")
    assert len(res_dash) == 1
    assert res_dash[0].habilidad == "Git"

    # Consulta con espacio
    res_space = await repo.get_by_ocupation("Desarrollador Software")
    assert len(res_space) == 1


@pytest.mark.asyncio
async def test_brecha_repository_get_all_ocupaciones(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica la lista de ocupaciones persistidas."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)

    await repo.save_habilidades(
        "dev_ops",
        [HabilidadComparada(habilidad="Docker", demanda=85.0, oferta_formativa=50.0)],
    )
    await repo.save_habilidades(
        "qa_engineer",
        [HabilidadComparada(habilidad="Selenium", demanda=75.0, oferta_formativa=60.0)],
    )

    ocupaciones = await repo.get_all_ocupaciones()
    assert "dev_ops" in ocupaciones
    assert "qa_engineer" in ocupaciones
