"""Inyectores de dependencias para los endpoints de la API."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.external_sync_service import ExternalSyncService
from app.application.services.file_upload_service import FileUploadService
from app.application.services.indice_empleabilidad_service import (
    IndiceEmpleabilidadService,
)
from app.application.validators.csv_file_validator import CsvFileValidator
from app.core.config import settings
from app.domain.interfaces.external_connector import IExternalDataConnector
from app.domain.interfaces.file_storage_service import IFileStorageService
from app.domain.interfaces.file_validator import IFileValidator
from app.domain.interfaces.indicador_repository import IIndicadorRepository
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)
from app.infrastructure.connectors.world_bank_connector import WorldBankConnector
from app.infrastructure.persistence.database import get_db_session
from app.infrastructure.persistence.repositories import (
    SqlAlchemyIndicadorRepository,
    SqlAlchemyIndiceEmpleabilidadRepository,
)
from app.infrastructure.storage.local_file_storage_service import (
    LocalFileStorageService,
)

from app.infrastructure.connectors.ilostat_connector import ILOSTATConnector

async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión de base de datos asíncrona por cada petición.

    Yields:
        AsyncSession: Sesión de SQLAlchemy lista para transacciones.
    """
    async for session in get_db_session():
        yield session


def provide_file_storage_service() -> IFileStorageService:
    """Provee la instancia del servicio de almacenamiento físico configurado.

    Returns:
        IFileStorageService: Implementación concreta de almacenamiento.
    """
    return LocalFileStorageService(base_dir=settings.upload_dir)


def provide_file_validator() -> IFileValidator:
    """Provee el validador de archivos configurado para CSV e ingesta.

    Returns:
        IFileValidator: Instancia de CsvFileValidator con límite de tamaño.
    """
    return CsvFileValidator(max_size_bytes=settings.max_upload_size_bytes)


def provide_file_upload_service(
    storage_service: Annotated[
        IFileStorageService,
        Depends(provide_file_storage_service),
    ],
    validator: Annotated[
        IFileValidator,
        Depends(provide_file_validator),
    ],
) -> FileUploadService:
    """Provee el servicio de aplicación para carga y persistencia de archivos.

    Args:
        storage_service: Servicio de almacenamiento inyectado por FastAPI.
        validator: Validador de reglas de negocio inyectado por FastAPI.

    Returns:
        FileUploadService: Servicio de aplicación inicializado.
    """
    return FileUploadService(
        storage_service=storage_service,
        validator=validator,
    )


def provide_indice_empleabilidad_repository(
    session: Annotated[
        AsyncSession,
        Depends(provide_db_session),
    ],
) -> IIndiceEmpleabilidadRepository:
    """Provee el repositorio para la consulta del Índice de Empleabilidad.

    Args:
        session: Sesión transaccional inyectada por FastAPI.

    Returns:
        IIndiceEmpleabilidadRepository: Instancia concreta del repositorio.
    """
    return SqlAlchemyIndiceEmpleabilidadRepository(session=session)


def provide_indice_empleabilidad_service(
    repository: Annotated[
        IIndiceEmpleabilidadRepository,
        Depends(provide_indice_empleabilidad_repository),
    ],
) -> IndiceEmpleabilidadService:
    """Provee el servicio de aplicación para el Índice de Empleabilidad.

    Args:
        repository: Repositorio inyectado por FastAPI.

    Returns:
        IndiceEmpleabilidadService: Servicio listo para su uso en controladores.
    """
    return IndiceEmpleabilidadService(repository=repository)


def provide_indicador_repository(
    session: Annotated[
        AsyncSession,
        Depends(provide_db_session),
    ],
) -> IIndicadorRepository:
    """Provee el repositorio para la persistencia y consulta de Indicadores.

    Args:
        session: Sesión transaccional inyectada por FastAPI.

    Returns:
        IIndicadorRepository: Instancia concreta de SqlAlchemyIndicadorRepository.
    """
    return SqlAlchemyIndicadorRepository(session=session)


def provide_world_bank_connector() -> IExternalDataConnector:
    """Provee la instancia del conector oficial de World Bank Indicators API.

    Returns:
        IExternalDataConnector: Instancia de WorldBankConnector configurada.
    """
    return WorldBankConnector(
        base_url=settings.world_bank_api_base_url,
        timeout=settings.world_bank_timeout_seconds,
    )


def provide_world_bank_sync_service(
    connector: Annotated[
        IExternalDataConnector,
        Depends(provide_world_bank_connector),
    ],
    repository: Annotated[
        IIndicadorRepository,
        Depends(provide_indicador_repository),
    ],
) -> ExternalSyncService:
    """Provee el servicio de aplicación para sincronización con World Bank.

    Args:
        connector: Conector de World Bank inyectado.
        repository: Repositorio de indicadores inyectado.

    Returns:
        ExternalSyncService: Servicio de aplicación listo para ejecución.
    """
    return ExternalSyncService(connector=connector, repository=repository)

def provide_ilostat_connector() -> IExternalDataConnector:
    """Provee una instancia del conector oficial de ILOSTAT."""
    return ILOSTATConnector()


def provide_ilostat_sync_service(
    connector: Annotated[
        IExternalDataConnector,
        Depends(provide_ilostat_connector),
    ],
    repository: Annotated[
        IIndicadorRepository,
        Depends(provide_indicador_repository),
    ],
) -> ExternalSyncService:
    """Provee el servicio de aplicación para sincronización con ILOSTAT.

    Args:
        connector: Conector de ILOSTAT inyectado.
        repository: Repositorio de indicadores inyectado.

    Returns:
        ExternalSyncService: Servicio de aplicación listo para ejecución.
    """
    return ExternalSyncService(connector=connector, repository=repository)