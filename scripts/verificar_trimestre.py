"""Script para verificar el estado de la columna trimestre en la base de datos."""

import asyncio
import os
import sys

# Asegurar backend en sys.path
backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend")
)
sys.path.insert(0, backend_path)

from sqlalchemy import text  # noqa: E402

from app.infrastructure.persistence.database import engine  # noqa: E402


async def main() -> None:
    """Ejecuta consultas de diagnóstico sobre la distribución de trimestres."""
    async with engine.connect() as conn:
        # 1. Verificar registros por trimestre
        query = text("""
            SELECT
                trimestre,
                COUNT(*) as cantidad,
                MIN(periodo) as ej_min,
                MAX(periodo) as ej_max
            FROM indicadores
            GROUP BY trimestre
            ORDER BY trimestre NULLS LAST
        """)
        result = await conn.execute(query)
        rows = result.fetchall()
        print("\n--- DISTRIBUCIÓN POR TRIMESTRE EN 'indicadores' ---")
        for r in rows:
            print(
                f"Trimestre: {str(r.trimestre):<8} | "
                f"Total: {r.cantidad:<5} | "
                f"Rango período: {r.ej_min} a {r.ej_max}"
            )

        # 2. Muestra de registros con trimestre
        sample_query = text("""
            SELECT id, pais, indicador, periodo, trimestre, valor, fuente
            FROM indicadores
            WHERE trimestre IS NOT NULL
            LIMIT 5
        """)
        sample_res = await conn.execute(sample_query)
        print("\n--- MUESTRA DE REGISTROS CON TRIMESTRE ---")
        for s in sample_res.fetchall():
            print(
                f"ID {s.id}: {s.pais} | {s.indicador} | "
                f"Período: {s.periodo} | Trimestre: {s.trimestre} | "
                f"Valor: {s.valor} | Fuente: {s.fuente}"
            )


if __name__ == "__main__":
    asyncio.run(main())
