"""Script de prueba y diagnóstico para el conector de SIMEL Chile.

Verifica:
1. Conectividad en vivo y diagnóstico del WAF de Huawei Cloud (HTTP 418).
2. Procesamiento y normalización del archivo CSV de ejemplo a RawIndicatorRecord.
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
    print(" 1. DIAGNÓSTICO EN VIVO: check_health() contra www.simel.gob.cl")
    print("==================================================================")
    healthy = await connector.check_health()
    print(f"Resultado de salud reportado: {healthy}")
    if not healthy:
        print(
            "-> Estado esperado: El portal de SIMEL Chile cuenta con protección\n"
            "   perimetral activa (Huawei Cloud WAF / HTTP 418) que restringe\n"
            "   solicitudes REST desatendidas."
        )
        print(
            "-> Alternativa operativa oficial: Ingesta de exportaciones CSV vía\n"
            "   POST /api/v1/ingesta/upload/simel"
        )
    else:
        print("-> El portal de SIMEL respondió exitosamente (HTTP 200).")

    print("\n==================================================================")
    print(" 2. PARSEO DE DATASET DE EJEMPLO: parse_simel_csv()")
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

    print(f"Total de registros normalizados: {len(records)}")

    indicadores_vistos: dict[str, int] = {}
    sectores_vistos: dict[str, int] = {}
    periodos_vistos: set[str] = set()

    for r in records:
        indicadores_vistos[r.indicador] = indicadores_vistos.get(r.indicador, 0) + 1
        if r.sector:
            sectores_vistos[r.sector] = sectores_vistos.get(r.sector, 0) + 1
        periodos_vistos.add(r.periodo)

    print("\nDistribución por indicador:")
    for ind, count in indicadores_vistos.items():
        print(f" - {ind}: {count} observaciones")

    print("\nDistribución por sector estratégico:")
    for sec, count in sectores_vistos.items():
        print(f" - {sec}: {count} observaciones")

    print(f"\nPeríodos cubiertos: {sorted(list(periodos_vistos))}")

    if records:
        print("\n--- Ejemplo de registro transformado (RawIndicatorRecord) ---")
        ej = records[0]
        print(f"País: {ej.pais}")
        print(f"Indicador: {ej.indicador}")
        print(f"Sector: {ej.sector}")
        print(f"Ocupación: {ej.ocupacion}")
        print(f"Período: {ej.periodo}")
        print(f"Valor: {ej.valor}")
        print(f"Tipo: {ej.tipo}")
        print(f"Fuente: {ej.fuente}")
        print(f"Metadatos: {ej.metadatos}")


if __name__ == "__main__":
    asyncio.run(main())
