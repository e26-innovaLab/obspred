"""Controlador y endpoints asociados a la consulta de tendencias y proyecciones."""

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.response_schema import create_success_response
from app.api.v1.schemas.tendencia_schema import (
    CambioSignificativo,
    MetadatosFuente,
    PuntoProyeccion,
    PuntoSerie,
    TendenciasDataSchema,
    TendenciasResponseSchema,
)
from app.core.constants import OPENAPI_TAG_TENDENCIAS, TENDENCIAS_ROUTE

tendencias_router = APIRouter(prefix=TENDENCIAS_ROUTE, tags=[OPENAPI_TAG_TENDENCIAS])


@tendencias_router.get(
    "",
    response_model=TendenciasResponseSchema,
    include_in_schema=False,
)
@tendencias_router.get(
    "/",
    response_model=TendenciasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obtener serie temporal, proyecciones y cambios significativos",
    description=(
        "Retorna la evolución histórica y proyectada para un país, sector, "
        "ocupación e indicador dados con el formato estándar ApiResponse."
    ),
)
async def get_tendencias(
    pais: str = Query(default="Argentina", description="Nombre del país o código ISO"),
    sector: str = Query(
        default="Todos los sectores",
        description="Sector de actividad económica",
    ),
    ocupacion: str = Query(
        default="Todas las ocupaciones",
        description="Categoría u ocupación laboral",
    ),
    indicador: str = Query(
        default="puestos_demandados",
        description="Tipo de indicador a consultar",
    ),
) -> TendenciasResponseSchema:
    """Procesa la consulta de tendencias y series temporales para el frontend.

    # TODO(backend): Conectar con TendenciaService / IndicadorRepository:
    # 1. Inyectar servicio de tendencias y proyecciones.
    # 2. Consultar serie histórica consolidada en base de datos.
    # 3. Computar cambios significativos y proyecciones estadísticas.

    Args:
        pais: País o código ISO solicitado.
        sector: Sector económico para filtrar.
        ocupacion: Denominación u ocupación de corte.
        indicador: Clave del indicador estadístico.

    Returns:
        TendenciasResponseSchema: Envoltorio estándar ApiResponse con los datos
            de tendencias y proyecciones.
    """
    data = TendenciasDataSchema(
        pais=pais,
        sector=sector,
        ocupacion=ocupacion,
        indicador=indicador,
        serie_historica=[
            PuntoSerie(periodo="T3 2023", valor=1620.0, es_destacado=False),
            PuntoSerie(periodo="T4 2023", valor=1750.0, es_destacado=True),  # Suba 8%
            PuntoSerie(periodo="T1 2024", valor=1768.0, es_destacado=False),
            PuntoSerie(periodo="T2 2024", valor=1760.0, es_destacado=False),
            PuntoSerie(periodo="T3 2024", valor=1758.0, es_destacado=False),
            PuntoSerie(periodo="T4 2024", valor=1835.0, es_destacado=False),
            PuntoSerie(periodo="T1 2025", valor=1868.0, es_destacado=False),
            PuntoSerie(periodo="T2 2025", valor=1852.0, es_destacado=False),
            PuntoSerie(periodo="T3 2025", valor=1826.0, es_destacado=False),
            PuntoSerie(periodo="T4 2025", valor=1860.0, es_destacado=False),
            PuntoSerie(periodo="T1 2026", valor=1820.0, es_destacado=False),
            PuntoSerie(periodo="T2 2026", valor=1933.0, es_destacado=True),  # Suba 6.2%
        ],
        cambios_significativos=[
            CambioSignificativo(
                periodo="T4 2023",
                titulo="Puestos demandados: suba de 8 %",
                descripcion="Variación respecto del período anterior (T3 2023).",
                tipo_alerta="warning",
            ),
            CambioSignificativo(
                periodo="T2 2026",
                titulo="Puestos demandados: suba de 6,2 %",
                descripcion="Variación respecto del período anterior (T1 2026).",
                tipo_alerta="warning",
            ),
        ],
        proyeccion=[
            PuntoProyeccion(
                periodo="T2 2026",
                valor_estimado=1933.0,
                valor_inferior=1933.0,
                valor_superior=1933.0,
            ),
            PuntoProyeccion(
                periodo="T3 2026",
                valor_estimado=1925.0,
                valor_inferior=1880.0,
                valor_superior=1980.0,
            ),
            PuntoProyeccion(
                periodo="T4 2026",
                valor_estimado=1940.0,
                valor_inferior=1870.0,
                valor_superior=2020.0,
            ),
        ],
        metadatos_historico=MetadatosFuente(fuente="CEPALSTAT", fecha="24/7/2026"),
        metadatos_proyeccion=MetadatosFuente(
            fuente="CEPALSTAT",
            fecha="24/7/2026",
            metodologia=(
                "Proyección orientativa (regresión lineal sobre la serie "
                "trimestral observada)."
            ),
        ),
    )

    return create_success_response(
        data=data,
        message="Tendencias y proyecciones obtenidas con éxito.",
        status_code=status.HTTP_200_OK,
    )
