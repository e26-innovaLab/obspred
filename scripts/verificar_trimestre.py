"""Script para verificar, limpiar y corregir el estado de periodo y trimestre en la base de datos."""

import argparse
import asyncio
import os
import sys

# Asegurar backend en sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

from app.infrastructure.persistence.database import engine
from sqlalchemy import text


async def diagnosticar() -> int:
    """Ejecuta consultas de diagnóstico sobre la distribución de periodos y trimestres.

    Returns:
        int: Cantidad de registros que presentan anomalías de formato.
    """
    async with engine.connect() as conn:
        print("\n========================================================")
        print(" DIAGNÓSTICO: DISTRIBUCIÓN POR TRIMESTRE EN 'indicadores'")
        print("========================================================")

        # 1. Distribución general de trimestres
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
        for r in rows:
            trim_display = r.trimestre if r.trimestre is not None else "NULL"
            print(
                f"Trimestre: {trim_display:<8} | "
                f"Total: {r.cantidad:<5} | "
                f"Rango período: {r.ej_min} a {r.ej_max}"
            )

        # 1.b. Verificar distribución y normalización de sectores
        query_sec = text("""
            SELECT
                sector,
                COUNT(*) as cantidad
            FROM indicadores
            GROUP BY sector
            ORDER BY sector NULLS LAST
        """)
        result_sec = await conn.execute(query_sec)
        rows_sec = result_sec.fetchall()
        print("\n========================================================")
        print(" DISTRIBUCIÓN POR SECTOR EN 'indicadores'")
        print("========================================================")
        for s in rows_sec:
            sec_display = s.sector if s.sector is not None else "NULL"
            print(f"Sector: {sec_display:<25} | Total: {s.cantidad:<5}")

        # 2. Detección de anomalías en el campo 'periodo' (fechas ISO o sufijos -QX)
        anomalies_query = text("""
            SELECT
                id, pais, indicador, periodo, trimestre, fuente
            FROM indicadores
            WHERE (periodo LIKE '____-__-__' OR periodo LIKE '%-Q%' OR periodo LIKE '%Q%')
              AND periodo != 'actual'
            ORDER BY id
        """)
        anomalies_res = await conn.execute(anomalies_query)
        anomalies = anomalies_res.fetchall()

        total_anomalias = len(anomalies)
        print("\n========================================================")
        print(
            f" ANÁLISIS DE FORMATO DE PERIODO (Anomalías detectadas: {total_anomalias})"
        )
        print("========================================================")

        if total_anomalias == 0:
            print(
                " [OK] Todos los registros cumplen con el formato canónico (año de 4 dígitos o catálogo)."
            )
        else:
            print(" [!] Se detectaron registros que requieren corrección:")
            for a in anomalies[:10]:
                print(
                    f" - ID {a.id}: {a.pais} | {a.indicador} | "
                    f"periodo='{a.periodo}' | trimestre={a.trimestre} | fuente='{a.fuente}'"
                )
            if total_anomalias > 10:
                print(f" ... y {total_anomalias - 10} registros más.")
            print(
                "\n [SUGERENCIA] Ejecute con la bandera --corregir para normalizar automáticamente."
            )

        # 3. Muestra de registros representativos corregidos
        sample_query = text("""
            SELECT id, pais, indicador, periodo, trimestre, valor, fuente
            FROM indicadores
            WHERE trimestre IS NOT NULL
            ORDER BY id DESC
            LIMIT 5
        """)
        sample_res = await conn.execute(sample_query)
        print("\n--- MUESTRA DE REGISTROS CON TRIMESTRE CALCULADO ---")
        for s in sample_res.fetchall():
            print(
                f"ID {s.id}: {s.pais} | {s.indicador} | "
                f"Período: {s.periodo} | Trimestre: {s.trimestre} | "
                f"Valor: {s.valor} | Fuente: {s.fuente}"
            )

        return total_anomalias


async def limpiar_y_corregir() -> None:
    """Corrige y normaliza registros en 'indicadores' de manera idempotente."""
    print("\n========================================================")
    print(" EJECUTANDO LIMPIEZA Y CORRECCIÓN DE PERIODOS Y TRIMESTRES")
    print("========================================================")

    async with engine.begin() as conn:
        # A. Series trimestrales con fecha ISO (YYYY-MM-DD):
        # Extrae el año para 'periodo' y calcula 'Q1'..'Q4' para 'trimestre' según el mes.
        sql_trim_iso = text("""
            UPDATE indicadores
            SET trimestre = 'Q' || (((CAST(SUBSTRING(periodo FROM 6 FOR 2) AS INT) - 1) / 3) + 1),
                periodo = SUBSTRING(periodo FROM 1 FOR 4)
            WHERE periodo LIKE '____-__-__'
              AND (
                  indicador IN ('empleo_registrado_total', 'empleo_registrado_industria', 'empleo_sector')
                  OR fuente IN ('Datos Argentina', 'SIMEL - INE Chile')
              )
        """)
        res_trim_iso = await conn.execute(sql_trim_iso)
        print(
            f" - Fechas ISO trimestrales convertidas (año + trimestre): {res_trim_iso.rowcount}"
        )

        # B. Series anuales con fecha ISO (YYYY-MM-DD):
        # Extrae el año para 'periodo' y asegura 'trimestre' en NULL.
        sql_anual_iso = text("""
            UPDATE indicadores
            SET trimestre = NULL,
                periodo = SUBSTRING(periodo FROM 1 FOR 4)
            WHERE periodo LIKE '____-__-__'
        """)
        res_anual_iso = await conn.execute(sql_anual_iso)
        print(
            f" - Fechas ISO anuales normalizadas (solo año): {res_anual_iso.rowcount}"
        )

        # C. Registros con sufijos trimestrales pegados al período (ej. '2024-Q1', '2024Q1'):
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            sql_q = text(f"""
                UPDATE indicadores
                SET trimestre = '{q}'
                WHERE (periodo LIKE '%-{q}%' OR periodo LIKE '%{q}%')
                  AND trimestre IS NULL
            """)
            await conn.execute(sql_q)

        # D. Limpieza de sufijos '-QX' del campo período para dejar exclusivamente el año:
        sql_clean_q = text("""
            UPDATE indicadores
            SET periodo = replace(replace(replace(replace(periodo, '-Q1', ''), '-Q2', ''), '-Q3', ''), '-Q4', '')
            WHERE periodo LIKE '%-Q%'
        """)
        res_clean_q = await conn.execute(sql_clean_q)
        print(f" - Sufijos '-QX' eliminados de 'periodo': {res_clean_q.rowcount}")

        # E. Normalización canónica de sectores (minúsculas y sin tildes):
        sectores_correcciones = {
            "Tecnología": "tecnologia",
            "Industria": "industria",
            "Servicios": "servicios",
            "Energía": "energia",
        }
        for orig, dest in sectores_correcciones.items():
            sql_sec = text(
                f"UPDATE indicadores SET sector = '{dest}' WHERE sector = '{orig}'"
            )
            res_sec = await conn.execute(sql_sec)
            if res_sec.rowcount > 0:
                print(
                    f" - Sector estandarizado '{orig}' -> '{dest}': {res_sec.rowcount}"
                )

    print("\n [OK] Limpieza y corrección finalizada exitosamente.")


async def main() -> None:
    """Punto de entrada principal con soporte de argumentos CLI."""
    parser = argparse.ArgumentParser(
        description="Herramienta de verificación, diagnóstico y corrección de periodos y trimestres."
    )
    parser.add_argument(
        "--corregir",
        "--limpiar",
        "--fix",
        action="store_true",
        dest="corregir",
        help="Aplica las correcciones automáticas sobre los registros mal formateados.",
    )
    args = parser.parse_args()

    if args.corregir:
        await limpiar_y_corregir()

    await diagnosticar()


if __name__ == "__main__":
    asyncio.run(main())
