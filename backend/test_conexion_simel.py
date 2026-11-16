"""Script de prueba y diagnóstico para el conector de SIMEL Chile.

Verifica:
1. Conectividad en vivo con la API oficial SDMX de SIMEL (.Stat Suite INE).
2. Extracción de indicadores en tiempo real desde sdmx.ine.gob.cl.
3. Procesamiento y normalización del archivo CSV de ejemplo a RawIndicatorRecord.
"""

import asyncio
from pathlib import Path

from app.infrastructure.connectors.simel_chile_connector import (
    SimelChileConnector,
)


async def main() -> None:
    """Ejecuta el flujo de diagnóstico y validación de SIMEL Chile."""
    connector = SimelChileConnector()

    print("==================================================================")
    print(" 1. DIAGNÓSTICO EN VIVO: check_health() contra sdmx.ine.gob.cl")
    print("==================================================================")
    healthy = await connector.check_health()
    print(f"Estado de API oficial SDMX (.Stat Suite): {healthy}")

    print("\n==================================================================")
    print(" 2. EXTRACCIÓN EN VIVO: fetch_indicators() para Chile (2024)")
    print("==================================================================")
    # Extrae indicadores oficiales en vivo filtrando desde 2024
    live_records = await connector.fetch_indicators(
        paises=["CHL"],
        indicadores=["tasa_desempleo", "empleo_sector"],
        periodo_desde="2024",
    )
    print(f"Total de registros obtenidos en vivo: {len(live_records)}")

    if live_records:
        indicadores_vistos: dict[str, int] = {}
        for r in live_records:
            indicadores_vistos[r.indicador] = indicadores_vistos.get(r.indicador, 0) + 1
        for ind, count in indicadores_vistos.items():
            print(f" - {ind}: {count} observaciones en vivo")

        ejemplo_vivo = live_records[0]
        print(f"\nEjemplo en vivo (País: {ejemplo_vivo.pais}):")
        print(f" - Indicador: {ejemplo_vivo.indicador}")
        print(f" - Sector: {ejemplo_vivo.sector}")
        print(f" - Período: {ejemplo_vivo.periodo}")
        print(f" - Valor: {ejemplo_vivo.valor}")
        print(f" - Fuente: {ejemplo_vivo.fuente}")

    print("\n==================================================================")
    print(" 3. PARSEO DE DATASET DE EJEMPLO: parse_simel_csv()")
    print("==================================================================")
    sample_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "examples"
        / "simel_chile_sample.csv"
    )

    if not sample_path.exists():
        print(f"No se encontró el archivo de ejemplo en: {sample_path}")
        return

    csv_bytes = sample_path.read_bytes()
    records = connector.parse_simel_csv(
        content=csv_bytes,
        filename=sample_path.name,
    )

    print(f"Total de registros normalizados del CSV: {len(records)}")

    sectores_vistos: dict[str, int] = {}
    for r in records:
        if r.sector:
            sectores_vistos[r.sector] = sectores_vistos.get(r.sector, 0) + 1

    print("\nDistribución por sector estratégico en CSV:")
    for sec, count in sectores_vistos.items():
        print(f" - {sec}: {count} observaciones")


if __name__ == "__main__":
    asyncio.run(main())
