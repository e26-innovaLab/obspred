"""Controlador y endpoints asociados al Índice de Empleabilidad por ocupación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies import provide_indice_empleabilidad_service
from app.api.v1.schemas.indice_empleabilidad_schema import (
    DimensionIndiceSchema,
    EvolucionIndicePuntoSchema,
    IndiceEmpleabilidadDataSchema,
    IndiceEmpleabilidadFilterSchema,
    IndiceEmpleabilidadResponseSchema,
    IndiceRankingDataSchema,
    IndiceRankingResponseSchema,
    OcupacionRankingItemDto,
)
from app.api.v1.schemas.response_schema import (
    ApiResponse,
    ResponseMeta,
    create_success_response,
)
from app.application.services.indice_empleabilidad_service import (
    IndiceEmpleabilidadService,
)
from app.core.constants import (
    INDICE_EMPLEABILIDAD_ROUTE,
    OPENAPI_TAG_INDICE_EMPLEABILIDAD,
)

indice_empleabilidad_router = APIRouter(
    prefix=INDICE_EMPLEABILIDAD_ROUTE,
    tags=[OPENAPI_TAG_INDICE_EMPLEABILIDAD],
)


@indice_empleabilidad_router.get(
    "/ranking",
    response_model=IndiceRankingResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Ranking tabular de ocupaciones por Índice de Empleabilidad",
    description=(
        "Retorna el listado de ocupaciones con puestos disponibles y score de "
        "empleabilidad para comparativas multi-país."
    ),
)
async def get_ranking_ocupaciones(
    pais: Annotated[
        str | None, Query(description="Códigos ISO-3 en CSV (ej. 'ARG,URY,CHL')")
    ] = None,
    sector: Annotated[
        str | None, Query(description="Filtro opcional de sector")
    ] = None,
    periodo: Annotated[str | None, Query(description="Período temporal")] = None,
) -> IndiceRankingResponseSchema:
    """Procesa el ranking de ocupaciones para la tabla de la vista Ocupaciones.

    Args:
        pais: Códigos ISO 3166-1 alpha-3 separados por coma.
        sector: Filtro opcional por sector estratégico.
        periodo: Período temporal de corte.

    Returns:
        IndiceRankingResponseSchema: Envoltorio ApiResponse con la lista clasificada
            de ocupaciones con puestos demandados y score de empleabilidad.
    """
    # TODO [backend]: Conectar con IndiceEmpleabilidadService:
    # 1. Inyectar IndiceEmpleabilidadService.get_ranking_multi_pais().
    # 2. Computar puestos demandados y score para ocupaciones por país.
    # 3. Ordenar descendentemente por puestos o score.
    paises_lista = (
        [p.strip().upper() for p in pais.split(",") if p.strip()]
        if pais
        else ["ARG", "URY", "CHL"]
    )

    mock_ocupaciones_base = [
        ("dev-software", "Desarrollador/a de software", 1820, 84.5),
        ("enfermeria", "Enfermero/a profesional", 1450, 78.0),
        ("analista-datos", "Analista de datos", 1210, 82.0),
        ("ing-renovables", "Ingeniero/a en energías renovables", 980, 75.5),
        ("especialista-ciberseguridad", "Especialista en ciberseguridad", 850, 86.0),
        ("product-manager", "Gerente de producto digital", 740, 79.5),
        ("tecnico-solar", "Técnico/a en instalaciones solares", 690, 71.0),
        ("kinesiologia", "Kinesiólogo/a y fisioterapeuta", 580, 68.5),
    ]

    items: list[OcupacionRankingItemDto] = []
    factor_pais = {"ARG": 1.0, "URY": 0.35, "CHL": 1.15}

    for p in paises_lista:
        factor = factor_pais.get(p, 1.0)
        for slug, nombre, vacantes, score in mock_ocupaciones_base:
            items.append(
                OcupacionRankingItemDto(
                    ocupacion_id=slug,
                    nombre=nombre,
                    puestos_disponibles=int(vacantes * factor),
                    indice_empleabilidad=min(
                        100.0, round(score * (0.95 if p == "URY" else 1.0), 1)
                    ),
                    pais=p,
                    fuente="innova.lab / Índices Armonizados",
                )
            )

    return create_success_response(
        data=IndiceRankingDataSchema(ocupaciones=items),
        message="Ranking de ocupaciones obtenido exitosamente.",
    )


@indice_empleabilidad_router.get(
    "/{ocupacion}",
    response_model=IndiceEmpleabilidadResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar Índice de Empleabilidad por ocupación",
    description=(
        "Obtiene el Índice de Empleabilidad multidimensional (score 0–100) "
        "para una ocupación específica, incluyendo el desglose de sus 4 "
        "dimensiones ponderadas, nivel cualitativo, trazabilidad total "
        "(fuente oficial, fecha de corte, tipo calculado) y serie histórica."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Índice de Empleabilidad obtenido con éxito.",
            "model": IndiceEmpleabilidadResponseSchema,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Parámetro de ocupación inválido o vacío.",
            "model": ApiResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "La ocupación solicitada no fue encontrada en el sistema.",
            "model": ApiResponse,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Error de validación sintáctica de parámetros.",
            "model": ApiResponse,
        },
    },
)
async def get_indice_empleabilidad_por_ocupacion(
    ocupacion: Annotated[
        str,
        Path(
            description=(
                "Identificador, slug o denominación de la ocupación (ej. dev-software)"
            ),
            min_length=1,
        ),
    ],
    filtros: Annotated[IndiceEmpleabilidadFilterSchema, Query()],
    service: Annotated[
        IndiceEmpleabilidadService,
        Depends(provide_indice_empleabilidad_service),
    ],
) -> IndiceEmpleabilidadResponseSchema:
    """Procesa la consulta del Índice de Empleabilidad para una ocupación.

    Args:
        ocupacion: Identificador o denominación de la ocupación requerida.
        filtros: Parámetros opcionales de filtrado (país, sector, período).
        service: Servicio de aplicación inyectado por FastAPI.

    Returns:
        IndiceEmpleabilidadResponseSchema: Envoltorio estándar ApiResponse con los datos
            del índice y metadatos con los filtros aplicados.
    """
    dto = await service.get_indice_por_ocupacion(
        ocupacion=ocupacion,
        pais=filtros.pais,
        sector=filtros.sector,
        periodo=filtros.periodo,
    )

    data = IndiceEmpleabilidadDataSchema(
        ocupacion_id=dto.ocupacion_id,
        ocupacion_nombre=dto.ocupacion_nombre,
        score=dto.score,
        nivel=dto.nivel,
        dimensiones=[
            DimensionIndiceSchema(
                nombre=dim.nombre,
                valor=dim.valor,
                peso=dim.peso,
                descripcion=dim.descripcion,
            )
            for dim in dto.dimensiones
        ],
        tipo=dto.tipo,
        fuente=dto.fuente,
        fecha_actualizacion=dto.fecha_actualizacion,
        metodologia=dto.metodologia,
        pais=dto.pais,
        sector=dto.sector,
        periodo=dto.periodo,
        evolucion=[
            EvolucionIndicePuntoSchema(
                periodo=evo.periodo,
                valor=evo.valor,
            )
            for evo in dto.evolucion
        ],
    )

    meta = ResponseMeta(
        total=1,
        extra={"filtros": filtros.model_dump()},
    )

    return create_success_response(
        data=data,
        message="Índice de Empleabilidad obtenido con éxito.",
        status_code=status.HTTP_200_OK,
        meta=meta,
    )
