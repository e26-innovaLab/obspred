"""Inyectores de dependencias para los endpoints de la API."""

from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.study_indicator_service import (
    StudyIndicatorService,
)
from app.domain.interfaces.study_indicator_repository import (
    StudyIndicatorRepositoryInterface,
)
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories import (
    fake_study_indicator_repository as fake_repo,
)


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión de base de datos asíncrona por cada petición.

    Yields:
        AsyncSession: Sesión de SQLAlchemy lista para transacciones.
    """
    async for session in get_db_session():
        yield session


# ============================================================================
# Dependencias para el servicio de estudio (StudyIndicatorService)
# ============================================================================

@lru_cache
def get_fake_study_indicator_repository() -> StudyIndicatorRepositoryInterface:
    """Provee una instancia compartida (singleton en memoria) del repositorio fake.

    En producción con DB real, este método construiría un SqlStudyIndicatorRepository
    inyectando la sesión `provide_db_session`.

    Returns:
        StudyIndicatorRepositoryInterface: Repositorio en memoria listo para operar.
    """
    return fake_repo.FakeStudyIndicatorRepository()


StudyIndicatorRepoDep = Annotated[
    StudyIndicatorRepositoryInterface, Depends(get_fake_study_indicator_repository)
]


def provide_study_indicator_service(
    repository: StudyIndicatorRepoDep,
) -> StudyIndicatorService:
    """Factoría que instancia el servicio inyectándole su repositorio.

    Args:
        repository: Repositorio inyectado automáticamente por FastAPI.

    Returns:
        StudyIndicatorService: Servicio configurado con su contrato de datos.
    """
    return StudyIndicatorService(repository=repository)


# Tipo anotado listo para usar directamente en la firma de cualquier endpoint
StudyIndicatorServiceDep = Annotated[
    StudyIndicatorService, Depends(provide_study_indicator_service)
]
