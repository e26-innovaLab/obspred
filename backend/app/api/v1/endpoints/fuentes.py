"""Controlador y endpoint para la auditoría y estado de fuentes y metodologías."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.fuentes_schema import (
    FuenteAuditoriaDto,
    FuentesDataSchema,
    FuentesResponseSchema,
    MetodologiaDto,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.constants import FUENTES_ROUTE, OPENAPI_TAG_FUENTES

fuentes_router = APIRouter(
    prefix=FUENTES_ROUTE,
    tags=[OPENAPI_TAG_FUENTES],
)


@fuentes_router.get(
    "",
    response_model=FuentesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Auditoría, estado de fuentes y metodologías",
    description=(
        "Retorna el inventario de fuentes oficiales con su frescura "
        "operativa y metodologías institucionales."
    ),
)
async def get_fuentes(
    pais: Annotated[
        str | None, Query(description="Filtrar fuentes por país (ISO-3)")
    ] = None,
) -> FuentesResponseSchema:
    """Procesa la consulta de fuentes y metodologías según Principio 3.

    Args:
        pais: Filtro opcional por código ISO 3166-1 alpha-3.

    Returns:
        FuentesResponseSchema: Envoltorio ApiResponse con la lista de fuentes
            oficiales auditadas y sus fichas metodológicas.
    """
    # TODO [backend]: Conectar con FuenteService / Auditoría de conectores (SyncLog):
    # 1. Inyectar servicio de auditoría de conectores (SyncLog / Conectores).
    # 2. Computar 'ultima_actualizacion' y 'estado_fuente' según logs de sync.
    # 3. Retornar las fichas metodológicas activas.
    fuentes_lista = [
        FuenteAuditoriaDto(
            id="ilostat",
            nombre="ILOSTAT — Organización Internacional del Trabajo (OIT)",
            descripcion=(
                "Series armonizadas de indicadores de empleo, desempleo y "
                "subutilización de la fuerza de trabajo."
            ),
            paises=["ARG", "URY", "CHL"],
            tipo_acceso="api",
            frecuencia="anual / trimestral",
            ultima_actualizacion="2026-09-30",
            proxima_actualizacion="2026-12-31",
            estado_fuente="activa",
            url="https://ilostat.ilo.org",
            indicadores_alimentados=[
                "Tasa de desempleo",
                "Tasa de empleo",
                "Participación laboral",
            ],
        ),
        FuenteAuditoriaDto(
            id="world-bank",
            nombre="World Bank Open Data — Banco Mundial",
            descripcion=(
                "Indicadores macroeconómicos y de desarrollo social comparables "
                "internacionalmente."
            ),
            paises=["ARG", "URY", "CHL"],
            tipo_acceso="api",
            frecuencia="anual",
            ultima_actualizacion="2026-08-15",
            proxima_actualizacion="2026-11-30",
            estado_fuente="activa",
            url="https://data.worldbank.org",
            indicadores_alimentados=["PIB per cápita", "Tasa de desempleo nacional"],
        ),
        FuenteAuditoriaDto(
            id="indec-eph",
            nombre="INDEC — Encuesta Permanente de Hogares (Argentina)",
            descripcion=(
                "Relevamiento continuo sobre mercado laboral, ingresos y "
                "condiciones socioeconómicas en Argentina."
            ),
            paises=["ARG"],
            tipo_acceso="dataset",
            frecuencia="trimestral",
            ultima_actualizacion="2026-09-24",
            proxima_actualizacion="2026-12-20",
            estado_fuente="activa",
            url="https://www.indec.gob.ar",
            indicadores_alimentados=[
                "Tasa de desempleo",
                "Empleo registrado",
                "Distribución de ingresos",
            ],
        ),
        FuenteAuditoriaDto(
            id="ine-chile-ene",
            nombre="INE Chile — Encuesta Nacional de Empleo y SIMEL",
            descripcion=(
                "Medición oficial y continua de la dinámica de ocupación, "
                "desocupación y formalidad en Chile."
            ),
            paises=["CHL"],
            tipo_acceso="api",
            frecuencia="trimestral móvil",
            ultima_actualizacion="2026-09-15",
            proxima_actualizacion="2026-10-31",
            estado_fuente="activa",
            url="https://www.ine.gob.cl",
            indicadores_alimentados=[
                "Tasa de desocupación",
                "Ocupados por rama de actividad",
            ],
        ),
        FuenteAuditoriaDto(
            id="ine-uruguay-ech",
            nombre="INE Uruguay — Encuesta Continua de Hogares",
            descripcion=(
                "Información representativa sobre actividad económica, empleo, "
                "salarios y hogares en Uruguay."
            ),
            paises=["URY"],
            tipo_acceso="dataset",
            frecuencia="mensual / semestral",
            ultima_actualizacion="2026-08-30",
            proxima_actualizacion="2026-11-15",
            estado_fuente="activa",
            url="https://www.ine.gub.uy",
            indicadores_alimentados=[
                "Tasa de empleo",
                "Tasa de desempleo",
                "Ingreso medio de los hogares",
            ],
        ),
        FuenteAuditoriaDto(
            id="sence-sabe",
            nombre="SENCE — Sistema de Análisis de Bolsas de Empleo (SABE Chile)",
            descripcion=(
                "Extracción sistemática y caracterización de competencias "
                "demandadas en ofertas laborales en línea."
            ),
            paises=["CHL"],
            tipo_acceso="dataset",
            frecuencia="mensual",
            ultima_actualizacion="2026-09-01",
            proxima_actualizacion="2026-10-28",
            estado_fuente="activa",
            url="https://sabe.sence.cl",
            indicadores_alimentados=[
                "Puestos demandados",
                "Habilidades más solicitadas",
                "Brechas formativas",
            ],
        ),
    ]

    metodologias_lista = [
        MetodologiaDto(
            id="indice-empleabilidad",
            titulo="Índice Multidimensional de Empleabilidad (v1.0)",
            resumen=(
                "Score ponderado (0-100) compuesto por: Demanda de puestos (35%), "
                "Estabilidad salarial (25%), Cobertura formativa (20%) y "
                "Crecimiento reciente (20%)."
            ),
            url="/docs/metodologia-indice-empleabilidad.md",
        ),
        MetodologiaDto(
            id="proyecciones-series",
            titulo="Proyecciones y Modelado Predictivo de Tendencias",
            resumen=(
                "Cálculo predictivo mediante regresiones sobre series temporales "
                "con exigencia de al menos 3 períodos históricos comparables y "
                "bandas de confianza al 80%."
            ),
            url="/docs/metodologia-proyecciones.md",
        ),
        MetodologiaDto(
            id="analisis-brechas",
            titulo="Matriz de Brechas Formativas y Habilidades Emergentes",
            resumen=(
                "Algoritmo de contraste entre la intensidad de búsqueda en "
                "vacantes de empleo y el flujo de egresados/titulaciones del "
                "sistema educativo formal."
            ),
            url="/docs/metodologia-brechas.md",
        ),
    ]

    if pais:
        pais_norm = pais.strip().upper()
        fuentes_lista = [f for f in fuentes_lista if pais_norm in f.paises]

    data = FuentesDataSchema(
        fuentes=fuentes_lista,
        metodologias=metodologias_lista,
    )

    return create_success_response(
        data=data,
        message="Información de trazabilidad y fuentes recuperada con éxito.",
    )
