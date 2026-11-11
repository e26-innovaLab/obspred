import asyncio
import logging

from app.infrastructure.connectors.datos_argentina_connector import (
    DatosArgentinaConnector,
)

logger = logging.getLogger(__name__)


async def main():
    connector = DatosArgentinaConnector()

    logger.info("--- 1. PROBANDO CONEXIÓN ---")

    health = await connector.check_health()
    logger.info("API disponible: %s", health)

    logger.info("--- 2. BUSCANDO SERIES ---")

    try:
        result = await connector.search_series(
            query="empleo",
            limit=5,
        )

        logger.info("Respuesta de la API:")
        logger.info("%s", result)

    except Exception:
        logger.exception("Error en la búsqueda")

    logger.info("--- 3. PROBANDO FETCH ---")

    try:
        records = await connector.fetch_indicators(
            paises=["ARG"],
            indicadores=list(
                DatosArgentinaConnector.INDICATOR_MAPPINGS.keys()
            ),
            periodo_desde="2018-01-01",
            periodo_hasta="2019-01-01",
        )

        logger.info("Registros obtenidos: %s", len(records))

        for record in records:
            logger.info("%s", record)

    except Exception:
        logger.exception("Error al obtener los indicadores")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(main())
