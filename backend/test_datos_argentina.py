import asyncio

from app.infrastructure.connectors.datos_argentina_connector import (
    DatosArgentinaConnector,
)


async def main():
    connector = DatosArgentinaConnector()

    print("\n--- 1. PROBANDO CONEXIÓN ---")

    health = await connector.check_health()
    print(f"API disponible: {health}")

    print("\n--- 2. BUSCANDO SERIES ---")

    try:
        result = await connector.search_series(
            query="empleo",
            limit=5,
        )

        print("Respuesta de la API:")
        print(result)

    except Exception as exc:
        print(f"Error en la búsqueda: {exc}")

    print("\n--- 3. PROBANDO FETCH ---")
    records = await connector.fetch_indicators(
        paises=["ARG"],
        indicadores=list(DatosArgentinaConnector.INDICATOR_MAPPINGS.keys()),
        periodo_desde="2018-01-01",
        periodo_hasta="2019-01-01",
    )

    print(f"Registros obtenidos: {len(records)}")

    for record in records:
        print(record)


if __name__ == "__main__":
    asyncio.run(main())
