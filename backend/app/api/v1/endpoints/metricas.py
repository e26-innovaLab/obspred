"""Controlador y endpoints asociados al módulo de métricas y gráficos."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.fuente_schema import FuenteItemSchema
from app.api.v1.schemas.metricas_schema import (
    ComparativaIndicadorDto,
    ComparativaValorPaisDto,
    KpiItemDto,
    MapaCalorCeldaDto,
    MapaCalorFilaDto,
    MetricasComparativaDataSchema,
    MetricasComparativaResponseSchema,
    MetricasKpisDataSchema,
    MetricasKpisResponseSchema,
    MetricasMapaCalorDataSchema,
    MetricasMapaCalorResponseSchema,
    MetricasProyeccionesDataSchema,
    MetricasProyeccionesResponseSchema,
    MetricasRankingDataSchema,
    MetricasRankingResponseSchema,
    MetricasSeriesDataSchema,
    MetricasSeriesResponseSchema,
    PuntoProyeccionDto,
    PuntoSerieDto,
    RankingItemDto,
    SerieItemDto,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.constants import METRICAS_ROUTE, OPENAPI_TAG_METRICAS

metricas_router = APIRouter(
    prefix=METRICAS_ROUTE,
    tags=[OPENAPI_TAG_METRICAS],
)


@metricas_router.get(
    "/series",
    response_model=MetricasSeriesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Series temporales multi-país para gráficos",
    description=(
        "Retorna una serie cronológica por cada país solicitado, lista para "
        "visualizaciones."
    ),
)
async def get_series(
    indicador: Annotated[
        str, Query(description="Slug del indicador", examples=["puestos_demandados"])
    ],
    pais: Annotated[
        str,
        Query(description="Códigos ISO-3 separados por coma", examples=["ARG,URY,CHL"]),
    ] = "ARG",
    sector: Annotated[str | None, Query(description="Slug del sector")] = None,
    ocupacion: Annotated[str | None, Query(description="Slug de la ocupación")] = None,
    desde: Annotated[str | None, Query(description="Período inicial")] = None,
    hasta: Annotated[str | None, Query(description="Período final")] = None,
    frecuencia: Annotated[
        str, Query(description="Periodicidad solicitada")
    ] = "trimestral",
) -> MetricasSeriesResponseSchema:
    """Procesa la consulta de series temporales multi-país.

    Args:
        indicador: Identificador o slug del indicador a graficar.
        pais: Uno o varios códigos ISO 3166-1 alpha-3 separados por coma.
        sector: Filtro opcional por sector estratégico.
        ocupacion: Filtro opcional por ocupación específica.
        desde: Período cronológico inicial (inclusive).
        hasta: Período cronológico final (inclusive).
        frecuencia: Periodicidad de agregación solicitada.

    Returns:
        MetricasSeriesResponseSchema: Envoltorio ApiResponse con la lista de series
            temporales y metadatos de trazabilidad.

    # TODO (Backend):
    # 1. Inyectar SeriesHistoricasService / Repositorio de indicadores.
    # 2. Reemplazar la generación de datos simulados por consulta SQL agrupada por país.
    # 3. Considerar frecuencia y filtro desde/hasta.
    """
    paises_lista = [p.strip().upper() for p in pais.split(",") if p.strip()]
    if not paises_lista:
        paises_lista = ["ARG"]

    series_data: list[SerieItemDto] = []
    fuente_base = FuenteItemSchema(
        fuente="Datos Oficiales Armonizados (INDEC / INE / SENCE)",
        fecha_actualizacion="2026-09-30",
        estado_fuente="activa",
        tipo="observado",
    )

    # Mock determinístico por país
    mock_valores = {
        "ARG": [
            ("2025-Q1", 1768.0),
            ("2025-Q2", 1760.0),
            ("2025-Q3", 1826.0),
            ("2025-Q4", 1860.0),
            ("2026-Q1", 1820.0),
            ("2026-Q2", 1933.0),
        ],
        "URY": [
            ("2025-Q1", 590.0),
            ("2025-Q2", 610.0),
            ("2025-Q3", 605.0),
            ("2025-Q4", 620.0),
            ("2026-Q1", 615.0),
            ("2026-Q2", 640.0),
        ],
        "CHL": [
            ("2025-Q1", 2100.0),
            ("2025-Q2", 2150.0),
            ("2025-Q3", 2200.0),
            ("2025-Q4", 2180.0),
            ("2026-Q1", 2250.0),
            ("2026-Q2", 2310.0),
        ],
    }

    for p in paises_lista:
        puntos = [
            PuntoSerieDto(periodo=per, valor=val, tipo="observado")
            for per, val in mock_valores.get(
                p, [("2026-Q1", 100.0), ("2026-Q2", 110.0)]
            )
        ]
        series_data.append(
            SerieItemDto(
                pais=p,
                indicador=indicador,
                nombre=indicador.replace("_", " ").capitalize(),
                unidad="avisos" if "puestos" in indicador else "%",
                frecuencia=frecuencia,
                puntos=puntos,
                fuentes=[fuente_base],
            )
        )

    return create_success_response(
        data=MetricasSeriesDataSchema(series=series_data),
        message="Series temporales recuperadas con éxito.",
    )


@metricas_router.get(
    "/proyecciones",
    response_model=MetricasProyeccionesResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Histórico y proyección a futuro con intervalos de confianza",
    description=(
        "Calcula la proyección estadística a corto plazo cumpliendo la regla "
        "de 3 períodos mínimos."
    ),
)
async def get_proyecciones(
    indicador: Annotated[
        str, Query(description="Slug del indicador", examples=["tasa_desempleo"])
    ],
    pais: Annotated[str, Query(description="Código ISO-3 (único)", examples=["ARG"])],
    sector: Annotated[str | None, Query(description="Slug de sector")] = None,
    ocupacion: Annotated[str | None, Query(description="Slug de ocupación")] = None,
    horizonte: Annotated[
        int, Query(description="Trimestres a proyectar (def: 2)", ge=1, le=8)
    ] = 2,
) -> MetricasProyeccionesResponseSchema:
    """Procesa el cálculo o consulta de proyecciones estadísticas.

    Args:
        indicador: Identificador del indicador a proyectar.
        pais: Código ISO 3166-1 alpha-3 del país.
        sector: Filtro opcional por sector estratégico.
        ocupacion: Filtro opcional por ocupación específica.
        horizonte: Cantidad de trimestres futuros a proyectar.

    Returns:
        MetricasProyeccionesResponseSchema: Envoltorio ApiResponse con la serie
            histórica, puntos proyectados e intervalos de confianza.

    # TODO (Backend):
    # 1. Inyectar servicio de modelado predictivo (regresión lineal o ARIMA).
    # 2. Aplicar validación de al menos 3 períodos históricos (Principio 5).
    # 3. Retornar límites superior e inferior calculados sobre la varianza muestral.
    """
    historico = [
        PuntoSerieDto(periodo="2025-Q1", valor=1868.0, tipo="observado"),
        PuntoSerieDto(periodo="2025-Q2", valor=1852.0, tipo="observado"),
        PuntoSerieDto(periodo="2025-Q3", valor=1826.0, tipo="observado"),
        PuntoSerieDto(periodo="2025-Q4", valor=1860.0, tipo="observado"),
        PuntoSerieDto(periodo="2026-Q1", valor=1820.0, tipo="observado"),
        PuntoSerieDto(periodo="2026-Q2", valor=1933.0, tipo="observado"),
    ]

    proyecciones = [
        PuntoProyeccionDto(
            periodo="2026-Q3",
            valor=1924.6,
            limite_inferior=1869.3,
            limite_superior=1979.9,
        ),
        PuntoProyeccionDto(
            periodo="2026-Q4",
            valor=1943.1,
            limite_inferior=1864.9,
            limite_superior=2021.3,
        ),
    ][:horizonte]

    data = MetricasProyeccionesDataSchema(
        pais=pais.upper(),
        indicador=indicador,
        unidad="avisos" if "puestos" in indicador else "%",
        historico=historico,
        proyeccion=proyecciones,
        proyectable=True,
        motivo_no_proyectable=None,
        metodo="Regresión lineal sobre serie trimestral observada",
        nivel_confianza=0.8,
        periodos_historicos=len(historico),
        fuentes=[
            FuenteItemSchema(
                fuente="innova.lab / Proyecciones estadísticas",
                fecha_actualizacion="2026-10-01",
                estado_fuente="activa",
                tipo="proyeccion",
                metodologia_url="/fuentes#proyecciones",
            )
        ],
    )

    return create_success_response(
        data=data,
        message="Proyección estadística calculada con éxito.",
    )


@metricas_router.get(
    "/kpis",
    response_model=MetricasKpisResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Tarjetas de indicadores clave (KPIs)",
    description=(
        "Devuelve el último valor, variación interperíodo y sparkline para "
        "los KPIs seleccionados."
    ),
)
async def get_kpis(
    indicadores: Annotated[str, Query(description="Slugs de indicadores en CSV")],
    pais: Annotated[str, Query(description="Código ISO-3 (único)", examples=["ARG"])],
    sector: Annotated[str | None, Query(description="Filtro de sector")] = None,
    ocupacion: Annotated[str | None, Query(description="Filtro de ocupación")] = None,
    periodo: Annotated[str | None, Query(description="Período de corte")] = None,
) -> MetricasKpisResponseSchema:
    """Procesa la obtención de métricas sintéticas y sparklines.

    Args:
        indicadores: Slugs de indicadores separados por coma.
        pais: Código ISO 3166-1 alpha-3 del país.
        sector: Filtro opcional por sector estratégico.
        ocupacion: Filtro opcional por ocupación específica.
        periodo: Período temporal de corte.

    Returns:
        MetricasKpisResponseSchema: Envoltorio ApiResponse con el resumen de KPIs,
            variaciones calculadas y sparklines.

    # TODO (Backend):
    # 1. Consultar últimos dos períodos disponibles por indicador en DB.
    # 2. Calcular variación absoluta y porcentual.
    # 3. Determinar tendencia según umbral acordado (±2%).
    # 4. Obtener serie de últimos 6-8 puntos para el sparkline.
    """
    indicadores_solicitados = [i.strip() for i in indicadores.split(",") if i.strip()]
    kpis_list: list[KpiItemDto] = []

    kpi_catalogo = {
        "tasa_desempleo": (
            "Tasa de desempleo",
            "%",
            7.6,
            7.9,
            -0.3,
            -3.8,
            "caida",
            "baja",
            [8.4, 8.2, 8.0, 7.9, 7.9, 7.6],
        ),
        "tasa_empleo": (
            "Tasa de empleo",
            "%",
            45.2,
            44.8,
            0.4,
            0.9,
            "crecimiento",
            "sube",
            [44.0, 44.2, 44.5, 44.7, 44.8, 45.2],
        ),
        "salario_real_indice": (
            "Salario real (Índice)",
            "pts",
            98.4,
            96.1,
            2.3,
            2.4,
            "crecimiento",
            "sube",
            [92.0, 93.5, 94.0, 95.2, 96.1, 98.4],
        ),
        "puestos_demandados": (
            "Puestos demandados",
            "avisos",
            1933.0,
            1820.0,
            113.0,
            6.2,
            "crecimiento",
            "sube",
            [1868.0, 1852.0, 1826.0, 1860.0, 1820.0, 1933.0],
        ),
    }

    fuente_kpi = FuenteItemSchema(
        fuente="INDEC / Encuesta Permanente de Hogares",
        fecha_actualizacion="2026-09-24",
        estado_fuente="activa",
        tipo="observado",
    )

    for ind in indicadores_solicitados:
        if ind in kpi_catalogo:
            nombre, unidad, val, val_ant, var_abs, var_pct, tend, sentido, spark = (
                kpi_catalogo[ind]
            )
            kpis_list.append(
                KpiItemDto(
                    indicador=ind,
                    nombre=nombre,
                    unidad=unidad,
                    periodo=periodo or "2026-Q2",
                    valor=val,
                    periodo_anterior="2026-Q1",
                    valor_anterior=val_ant,
                    variacion_abs=var_abs,
                    variacion_pct=var_pct,
                    tendencia=tend,  # type: ignore[arg-type]
                    sentido_positivo=sentido,  # type: ignore[arg-type]
                    sparkline=spark,
                    fuente=fuente_kpi,
                )
            )

    return create_success_response(
        data=MetricasKpisDataSchema(kpis=kpis_list),
        message="KPIs recuperados exitosamente.",
    )


@metricas_router.get(
    "/ranking",
    response_model=MetricasRankingResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Clasificación y ranking por dimensión",
    description=(
        "Ranking ordenado de sectores, ocupaciones o habilidades según "
        "valor o variación."
    ),
)
async def get_ranking(
    dimension: Annotated[
        str, Query(description="sector, ocupacion o habilidad", examples=["sector"])
    ],
    indicador: Annotated[
        str, Query(description="Indicador a ordenar", examples=["puestos_demandados"])
    ],
    pais: Annotated[str, Query(description="Código ISO-3 (único)", examples=["ARG"])],
    sector: Annotated[
        str | None, Query(description="Filtro de sector si la dimensión es ocupación")
    ] = None,
    periodo: Annotated[str | None, Query(description="Período temporal")] = None,
    orden: Annotated[str, Query(description="'valor' o 'variacion'")] = "valor",
    limite: Annotated[int, Query(description="Cantidad de registros", ge=1, le=20)] = 5,
) -> MetricasRankingResponseSchema:
    """Procesa rankings por dimensión.

    Args:
        dimension: Dimensión analítica ('sector', 'ocupacion' o 'habilidad').
        indicador: Indicador utilizado para la clasificación.
        pais: Código ISO 3166-1 alpha-3 del país.
        sector: Filtro opcional por sector si la dimensión es ocupación.
        periodo: Período temporal de referencia.
        orden: Criterio de ordenamiento ('valor' o 'variacion').
        limite: Cantidad máxima de registros a retornar.

    Returns:
        MetricasRankingResponseSchema: Envoltorio ApiResponse con los ítems ordenados
            y sus fuentes de información.

    # TODO (Backend):
    # 1. Ejecutar consulta SQL agregada por la dimensión requerida.
    # 2. Ordenar por valor o variación porcentual descendente según query param.
    # 3. Aplicar límite de registros.
    """
    items_mock = {
        "sector": [
            RankingItemDto(
                id="tecnologia",
                nombre="Tecnología",
                valor=3120.0,
                variacion_pct=8.4,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="salud",
                nombre="Salud",
                valor=2875.0,
                variacion_pct=1.1,
                tendencia="estabilidad",
            ),
            RankingItemDto(
                id="energia",
                nombre="Energía",
                valor=1940.0,
                variacion_pct=4.2,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="turismo",
                nombre="Turismo",
                valor=1650.0,
                variacion_pct=-2.5,
                tendencia="caida",
            ),
            RankingItemDto(
                id="economia-conocimiento",
                nombre="Economía del Conocimiento",
                valor=1420.0,
                variacion_pct=5.0,
                tendencia="crecimiento",
            ),
        ],
        "ocupacion": [
            RankingItemDto(
                id="dev-software",
                nombre="Desarrollador/a de software",
                valor=1820.0,
                variacion_pct=9.1,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="enfermeria",
                nombre="Enfermero/a profesional",
                valor=1450.0,
                variacion_pct=2.0,
                tendencia="estabilidad",
            ),
            RankingItemDto(
                id="analista-datos",
                nombre="Analista de datos",
                valor=1210.0,
                variacion_pct=12.4,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="ing-renovables",
                nombre="Ingeniero/a en energías renovables",
                valor=980.0,
                variacion_pct=7.2,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="especialista-ciberseguridad",
                nombre="Especialista en ciberseguridad",
                valor=850.0,
                variacion_pct=15.1,
                tendencia="crecimiento",
            ),
        ],
        "habilidad": [
            RankingItemDto(
                id="cloud-computing",
                nombre="Cloud computing",
                valor=92.0,
                variacion_pct=14.0,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="analisis-datos",
                nombre="Análisis de datos",
                valor=88.0,
                variacion_pct=10.2,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="ia-generativa",
                nombre="IA aplicada",
                valor=85.0,
                variacion_pct=25.4,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="ciberseguridad",
                nombre="Ciberseguridad",
                valor=79.0,
                variacion_pct=8.0,
                tendencia="crecimiento",
            ),
            RankingItemDto(
                id="devops",
                nombre="DevOps / CI-CD",
                valor=74.0,
                variacion_pct=6.5,
                tendencia="crecimiento",
            ),
        ],
    }

    seleccionados = items_mock.get(dimension, items_mock["sector"])[:limite]

    fuente_ranking = FuenteItemSchema(
        fuente="SENCE / SABE / Portales de empleo oficiales",
        fecha_actualizacion="2026-09-01",
        estado_fuente="activa",
        tipo="observado",
    )

    data = MetricasRankingDataSchema(
        dimension=dimension,
        indicador=indicador,
        unidad="avisos" if dimension != "habilidad" else "score",
        periodo=periodo or "2026-Q2",
        items=seleccionados,
        fuentes=[fuente_ranking],
    )

    return create_success_response(
        data=data,
        message=f"Ranking por dimensión '{dimension}' obtenido exitosamente.",
    )


@metricas_router.get(
    "/comparativa",
    response_model=MetricasComparativaResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Tarjetas comparativas por indicador entre países",
    description=(
        "Retorna el último valor registrado de cada país para una lista de indicadores."
    ),
)
async def get_comparativa(
    indicadores: Annotated[str, Query(description="Slugs de indicadores en CSV")],
    pais: Annotated[
        str, Query(description="Códigos ISO-3 en CSV", examples=["ARG,URY,CHL"])
    ],
    sector: Annotated[
        str | None, Query(description="Filtro opcional de sector")
    ] = None,
) -> MetricasComparativaResponseSchema:
    """Procesa tarjetas comparativas multi-país.

    Args:
        indicadores: Slugs de indicadores separados por coma.
        pais: Códigos ISO 3166-1 alpha-3 separados por coma.
        sector: Filtro opcional por sector estratégico.

    Returns:
        MetricasComparativaResponseSchema: Envoltorio ApiResponse con la comparativa
            del último valor de cada país por indicador.

    # TODO (Backend):
    # 1. Buscar último valor reportado en cada país para cada indicador.
    # 2. Respetar frecuencias y períodos de corte distintos entre países.
    """
    paises_solicitados = [p.strip().upper() for p in pais.split(",") if p.strip()]
    indicadores_solicitados = [i.strip() for i in indicadores.split(",") if i.strip()]

    comparativas: list[ComparativaIndicadorDto] = []

    mock_db = {
        "tasa_desempleo": {
            "nombre": "Tasa de desempleo",
            "unidad": "%",
            "valores": {
                "ARG": (7.6, "2026-Q2", "INDEC — EPH"),
                "URY": (7.9, "2025", "INE Uruguay — ECH"),
                "CHL": (8.3, "2026-Q1", "INE Chile — ENE"),
            },
        },
        "tasa_empleo": {
            "nombre": "Tasa de empleo",
            "unidad": "%",
            "valores": {
                "ARG": (45.2, "2026-Q2", "INDEC — EPH"),
                "URY": (58.4, "2025", "INE Uruguay — ECH"),
                "CHL": (56.1, "2026-Q1", "INE Chile — ENE"),
            },
        },
        "salario_real_indice": {
            "nombre": "Salario real (Índice)",
            "unidad": "pts",
            "valores": {
                "ARG": (98.4, "2026-Q2", "Secretaría de Trabajo"),
                "URY": (104.2, "2025", "INE Uruguay"),
                "CHL": (102.0, "2026-Q1", "Banco Central de Chile"),
            },
        },
    }

    for ind in indicadores_solicitados:
        info = mock_db.get(
            ind,
            {
                "nombre": ind.replace("_", " ").capitalize(),
                "unidad": "%",
                "valores": {},
            },
        )
        valores_pais: list[ComparativaValorPaisDto] = []

        for p in paises_solicitados:
            if p in info["valores"]:
                val, per, fuente_nombre = info["valores"][p]
                valores_pais.append(
                    ComparativaValorPaisDto(
                        pais=p,
                        valor=val,
                        periodo=per,
                        fuente=FuenteItemSchema(
                            fuente=fuente_nombre,
                            fecha_actualizacion="2026-09-30",
                            estado_fuente="activa",
                            tipo="observado",
                        ),
                    )
                )
            else:
                valores_pais.append(
                    ComparativaValorPaisDto(
                        pais=p, valor=None, periodo=None, fuente=None
                    )
                )

        comparativas.append(
            ComparativaIndicadorDto(
                indicador=ind,
                nombre=info["nombre"],
                unidad=info["unidad"],
                valores=valores_pais,
            )
        )

    return create_success_response(
        data=MetricasComparativaDataSchema(indicadores=comparativas),
        message="Comparativa entre países recuperada exitosamente.",
    )


@metricas_router.get(
    "/mapa-calor",
    response_model=MetricasMapaCalorResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Matriz sector × país de un indicador",
    description="Genera la grilla de celdas para el mapa de calor.",
)
async def get_mapa_calor(
    indicador: Annotated[
        str, Query(description="Slug del indicador", examples=["tasa_desempleo"])
    ],
    pais: Annotated[
        str, Query(description="Códigos ISO-3 en CSV", examples=["ARG,URY,CHL"])
    ],
    filas: Annotated[
        str, Query(description="Dimensión de las filas (def: sector)")
    ] = "sector",
    periodo: Annotated[str | None, Query(description="Período de análisis")] = None,
) -> MetricasMapaCalorResponseSchema:
    """Procesa la grilla para el mapa de calor.

    Args:
        indicador: Identificador del indicador a evaluar en la matriz.
        pais: Códigos ISO 3166-1 alpha-3 separados por coma (columnas).
        filas: Dimensión de las filas (def: 'sector').
        periodo: Período temporal de análisis.

    Returns:
        MetricasMapaCalorResponseSchema: Envoltorio ApiResponse con la estructura
            matricial de celdas para el mapa de calor.

    # TODO (Backend):
    # 1. Cruzar registros de la base agrupando por sector (fila) y país (columna).
    # 2. Retornar celdas completas, incluso las vacías con valor null.
    """
    paises_col = [p.strip().upper() for p in pais.split(",") if p.strip()]

    filas_sectores = [
        MapaCalorFilaDto(id="tecnologia", nombre="Tecnología"),
        MapaCalorFilaDto(id="salud", nombre="Salud"),
        MapaCalorFilaDto(id="energia", nombre="Energía"),
        MapaCalorFilaDto(id="turismo", nombre="Turismo"),
        MapaCalorFilaDto(
            id="economia-conocimiento", nombre="Economía del Conocimiento"
        ),
    ]

    celdas: list[MapaCalorCeldaDto] = []
    matriz_mock = {
        ("tecnologia", "ARG"): (6.2, 5.8),
        ("tecnologia", "URY"): (5.4, -1.2),
        ("tecnologia", "CHL"): (5.9, 2.1),
        ("salud", "ARG"): (7.1, 0.5),
        ("salud", "URY"): (6.8, 1.0),
        ("salud", "CHL"): (6.5, -0.4),
        ("energia", "ARG"): (5.0, 3.2),
        ("energia", "URY"): (None, None),
        ("energia", "CHL"): (4.8, 1.1),
        ("turismo", "ARG"): (8.9, -2.0),
        ("turismo", "URY"): (8.1, 0.2),
        ("turismo", "CHL"): (7.5, -1.5),
        ("economia-conocimiento", "ARG"): (5.8, 4.1),
        ("economia-conocimiento", "URY"): (5.2, 1.8),
        ("economia-conocimiento", "CHL"): (5.5, 3.0),
    }

    for f in filas_sectores:
        for c in paises_col:
            valor, var = matriz_mock.get((f.id, c), (None, None))
            celdas.append(
                MapaCalorCeldaDto(fila=f.id, columna=c, valor=valor, variacion_pct=var)
            )

    data = MetricasMapaCalorDataSchema(
        indicador=indicador,
        nombre=indicador.replace("_", " ").capitalize(),
        unidad="%",
        periodo=periodo or "2026-Q2",
        filas=filas_sectores,
        columnas=paises_col,
        celdas=celdas,
        fuentes=[
            FuenteItemSchema(
                fuente="ILOSTAT / CEPALSTAT Armonizado",
                fecha_actualizacion="2026-09-30",
                estado_fuente="activa",
                tipo="observado",
            )
        ],
    )

    return create_success_response(
        data=data,
        message="Mapa de calor generado exitosamente.",
    )
