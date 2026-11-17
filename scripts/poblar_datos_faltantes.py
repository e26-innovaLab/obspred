"""Script para poblar registros faltantes en la base de datos del Observatorio.

Puebla:
1. Catálogo oficial de fuentes de información (tabla 'fuentes').
2. Catálogo completo de brechas de habilidades (tabla 'habilidades_brechas').
3. Indicadores de Datos Argentina (series de empleo registrado y EPH).
4. Taxonomías y metadatos de ESCO (tabla 'indicadores').
5. Muestra completa de SIMEL Chile (tabla 'indicadores').
6. Indicadores del Banco Mundial (World Bank) para Argentina, Uruguay y Chile.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Asegurar backend en sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

from app.application.services.brecha_service import BrechaService
from app.application.services.catalogo_service import CatalogoService
from app.application.services.external_sync_service import ExternalSyncService
from app.core.constants import FuenteEstado
from app.infrastructure.connectors.datos_argentina_connector import (
    DatosArgentinaConnector,
)
from app.infrastructure.connectors.esco_connector import EscoConnector
from app.infrastructure.connectors.simel_chile_connector import SimelChileConnector
from app.infrastructure.connectors.world_bank_connector import WorldBankConnector
from app.infrastructure.persistence.database import async_session_factory
from app.infrastructure.persistence.models.fuente import FuenteModel
from app.infrastructure.persistence.repositories.brecha_repository import (
    SQLAlchemyBrechaRepository,
)
from app.infrastructure.persistence.repositories.catalogo_repository import (
    SqlAlchemyCatalogoRepository,
)
from app.infrastructure.persistence.repositories.indicador_repository import (
    SqlAlchemyIndicadorRepository,
)
from sqlalchemy import select, text

FUENTES_SEMILLA = [
    {
        "nombre": "Datos Argentina — Series de Tiempo",
        "descripcion": "API de series de tiempo de la Secretaría de Innovación Pública de Argentina.",
        "url": "https://apis.datos.gob.ar/series/api",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "INDEC — Encuesta Permanente de Hogares (EPH)",
        "descripcion": "Encuesta sobre empleo y condiciones de vida en aglomerados urbanos de Argentina.",
        "url": "https://www.indec.gob.ar",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "Secretaría de Trabajo — Empleo Registrado",
        "descripcion": "Estadísticas del empleo asalariado registrado del sector privado y salarios (SIPA).",
        "url": "https://www.argentina.gob.ar/trabajo",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "World Bank",
        "descripcion": "Base de datos global de indicadores socioeconómicos del Banco Mundial.",
        "url": "https://data.worldbank.org",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "ILOSTAT",
        "descripcion": "Base de datos estadística de la Organización Internacional del Trabajo (OIT).",
        "url": "https://ilostat.ilo.org",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "CEPALSTAT",
        "descripcion": "Portal de estadísticas e indicadores de América Latina y el Caribe (CEPAL).",
        "url": "https://statistics.cepal.org/portal/cepalstat",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "SIMEL - INE Chile",
        "descripcion": "Sistema de Información sobre el Mercado Laboral de Chile (INE y Mesa de Trabajo Decente).",
        "url": "https://www.simel.gob.cl",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "Banco Central de Chile",
        "descripcion": "Servicios de Información Estadística (SIETE) y series macroeconómicas y financieras.",
        "url": "https://si3.bcentral.cl",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "SENCE — Sistema de Análisis de Bolsas de Empleo (SABE)",
        "descripcion": "Análisis de vacantes y competencias laborales en portales web de empleo en Chile.",
        "url": "https://sence.gob.cl",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "INE Uruguay — ECH",
        "descripcion": "Encuesta Continua de Hogares del Instituto Nacional de Estadística de Uruguay.",
        "url": "https://www.ine.gub.uy",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "ANEP — Observatorio de la Educación",
        "descripcion": "Administración Nacional de Educación Pública y DGETP-UTU de Uruguay.",
        "url": "https://www.anep.edu.uy",
        "estado": FuenteEstado.ACTIVA,
    },
    {
        "nombre": "ESCO",
        "descripcion": "Clasificación europea multilingüe de competencias, cualificaciones y ocupaciones.",
        "url": "https://ec.europa.eu/esco",
        "estado": FuenteEstado.ACTIVA,
    },
]


async def poblar_catalogo_maestro(session) -> dict[str, int]:
    """Puebla de manera idempotente las tablas maestras del catálogo."""
    print("\n--- 1. POBLANDO TABLAS MAESTRAS DEL CATÁLOGO ---")
    repo = SqlAlchemyCatalogoRepository(session=session)
    service = CatalogoService(repository=repo)
    stats = await service.seed_catalogo()
    print(f"Catálogo maestro sembrado con éxito: {stats}")
    return stats


async def poblar_fuentes(session) -> int:
    """Puebla el catálogo de fuentes oficiales de forma idempotente."""
    print("\n--- 2. POBLANDO TABLA 'fuentes' ---")
    ahora = datetime.now(timezone.utc)
    insertadas = 0

    for f_data in FUENTES_SEMILLA:
        stmt = select(FuenteModel).where(FuenteModel.nombre == f_data["nombre"])
        res = await session.execute(stmt)
        existente = res.scalar_one_or_none()

        if existente is None:
            nueva = FuenteModel(
                nombre=f_data["nombre"],
                descripcion=f_data["descripcion"],
                url=f_data["url"],
                estado=f_data["estado"],
                ultima_actualizacion=ahora,
            )
            session.add(nueva)
            insertadas += 1
            print(f" [+] Insertada fuente: {f_data['nombre']}")
        else:
            print(f" [=] Fuente ya existente: {f_data['nombre']}")

    await session.commit()
    print(f"Total fuentes nuevas insertadas: {insertadas}")
    return insertadas


async def poblar_brechas(session) -> int:
    """Puebla el catálogo de brechas de habilidades."""
    print("\n--- 2. POBLANDO TABLA 'habilidades_brechas' ---")
    repo = SQLAlchemyBrechaRepository(db=session)
    service = BrechaService(repository=repo)
    total_ocupaciones = await service.seed_catalogo()
    await session.commit()
    print(f"Catálogo de brechas sembrado con éxito: {total_ocupaciones} ocupaciones.")
    return total_ocupaciones


async def poblar_simel_csv(session) -> int:
    """Puebla los registros del CSV de muestra de SIMEL Chile."""
    print("\n--- 3. POBLANDO SIMEL CHILE (MUESTRA CSV) ---")
    sample_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "examples"
        / "simel_chile_sample.csv"
    )

    if not sample_path.exists():
        print(f" [!] Archivo no encontrado: {sample_path}")
        return 0

    connector = SimelChileConnector()
    csv_bytes = sample_path.read_bytes()
    records = connector.parse_simel_csv(content=csv_bytes, filename=sample_path.name)
    print(f"Registros normalizados del CSV SIMEL: {len(records)}")

    repo = SqlAlchemyIndicadorRepository(session=session)
    guardados = await repo.upsert_batch(records)
    await session.commit()
    print(f"Registros SIMEL guardados/actualizados: {guardados}")
    return guardados


async def sincronizar_datos_argentina(session) -> int:
    """Sincroniza indicadores oficiales desde Datos Argentina."""
    print("\n--- 4. SINCRONIZANDO DATOS ARGENTINA ---")
    connector = DatosArgentinaConnector()
    repo = SqlAlchemyIndicadorRepository(session=session)
    sync_service = ExternalSyncService(connector=connector, repository=repo)

    result = await sync_service.sync_data(
        periodo_desde="2018-01-01",
        periodo_hasta="2026-01-01",
    )
    await session.commit()
    print(
        f"Datos Argentina: {result.total_fetched} obtenidos, "
        f"{result.total_persisted} guardados ({result.status.value})"
    )
    return result.total_persisted


async def sincronizar_esco(session) -> int:
    """Sincroniza taxonomías ocupacionales desde ESCO."""
    print("\n--- 5. SINCRONIZANDO TAXONOMÍAS ESCO ---")
    connector = EscoConnector()
    repo = SqlAlchemyIndicadorRepository(session=session)
    sync_service = ExternalSyncService(connector=connector, repository=repo)

    result = await sync_service.sync_data()
    await session.commit()
    print(
        f"ESCO: {result.total_fetched} obtenidos, "
        f"{result.total_persisted} guardados ({result.status.value})"
    )
    return result.total_persisted


async def sincronizar_world_bank(session) -> int:
    """Sincroniza indicadores del Banco Mundial para ARG, URY y CHL."""
    print("\n--- 6. SINCRONIZANDO BANCO MUNDIAL ---")
    connector = WorldBankConnector()
    repo = SqlAlchemyIndicadorRepository(session=session)
    sync_service = ExternalSyncService(connector=connector, repository=repo)

    result = await sync_service.sync_data(
        paises=["ARG", "URY", "CHL"],
        periodo_desde="2018",
        periodo_hasta="2025",
    )
    await session.commit()
    print(
        f"Banco Mundial: {result.total_fetched} obtenidos, "
        f"{result.total_persisted} guardados ({result.status.value})"
    )
    return result.total_persisted


async def main() -> None:
    """Función principal orquestadora del poblado."""
    print("==========================================================")
    print(" INICIO DE POBLADO DE REGISTROS FALTANTES")
    print("==========================================================")

    async with async_session_factory() as session:
        # 0. Catálogo maestro
        await poblar_catalogo_maestro(session)

        # 1. Fuentes
        await poblar_fuentes(session)

        # 2. Brechas de habilidades
        await poblar_brechas(session)

        # 3. SIMEL CSV
        await poblar_simel_csv(session)

        # 4. Datos Argentina
        try:
            await sincronizar_datos_argentina(session)
        except Exception as exc:  # noqa: BLE001
            print(f" [!] Error al sincronizar Datos Argentina: {exc}")

        # 5. ESCO
        try:
            await sincronizar_esco(session)
        except Exception as exc:  # noqa: BLE001
            print(f" [!] Error al sincronizar ESCO: {exc}")

        # 6. Banco Mundial
        try:
            await sincronizar_world_bank(session)
        except Exception as exc:  # noqa: BLE001
            print(f" [!] Error al sincronizar Banco Mundial: {exc}")

    print("\n==========================================================")
    print(" RESUMEN FINAL DEL ESTADO DE LA BASE DE DATOS")
    print("==========================================================")
    async with async_session_factory() as session:
        f_count = (await session.execute(text("SELECT COUNT(*) FROM fuentes"))).scalar()
        h_count = (await session.execute(text("SELECT COUNT(*) FROM habilidades_brechas"))).scalar()
        i_count = (await session.execute(text("SELECT COUNT(*) FROM indicadores"))).scalar()
        print(f"Total en 'fuentes': {f_count}")
        print(f"Total en 'habilidades_brechas': {h_count}")
        print(f"Total en 'indicadores': {i_count}")

        fuentes_dist = (await session.execute(text("SELECT fuente, COUNT(*) FROM indicadores GROUP BY fuente ORDER BY COUNT(*) DESC"))).fetchall()
        print("\nDistribución por fuente en 'indicadores':")
        for f, cnt in fuentes_dist:
            print(f" - {f}: {cnt} registros")


if __name__ == "__main__":
    asyncio.run(main())
