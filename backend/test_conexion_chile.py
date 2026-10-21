import asyncio
from app.infrastructure.connectors.bcentral_chile_connector import (
    BCentralChileConnector,
)


async def main():
    connector = BCentralChileConnector()

    print("--- 1. Probando check_health() ---")
    healthy = await connector.check_health()
    print(f"Estado de conexión / salud: {healthy}")

    if not healthy:
        print("La verificación de salud falló. Revisá credenciales o conexión.")
        return

    print("\n--- 2. Probando fetch_indicators() para Chile ---")
    # Consulta las 5 series configuradas para el primer semestre de 2024
    records = await connector.fetch_indicators(
        paises=["CHL"],
        periodo_desde="2024",
        periodo_hasta="2024",
    )

    print(f"Total registros obtenidos: {len(records)}")

    # Mostramos un resumen por indicador
    indicadores_vistos = {}
    for r in records:
        indicadores_vistos[r.indicador] = indicadores_vistos.get(r.indicador, 0) + 1

    print("\nDistribución por indicador:")
    for ind, count in indicadores_vistos.items():
        print(f" - {ind}: {count} observaciones")

    if records:
        print("\n--- Ejemplo de registro transformado (RawIndicatorRecord) ---")
        ejemplo = records[0]
        print(f"País: {ejemplo.pais}")
        print(f"Indicador: {ejemplo.indicador}")
        print(f"Período: {ejemplo.periodo}")
        print(f"Valor: {ejemplo.valor}")
        print(f"Fuente: {ejemplo.fuente}")
        print(f"Metadatos: {ejemplo.metadatos}")


if __name__ == "__main__":
    asyncio.run(main())
