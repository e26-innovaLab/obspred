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
    ERROR_MSG_PAIS_NO_RECONOCIDO_TEMPLATE,
    INDICE_EMPLEABILIDAD_GET_SUCCESS_MESSAGE,
    INDICE_EMPLEABILIDAD_OCUPACION_ROUTE,
    INDICE_EMPLEABILIDAD_RANKING_ROUTE,
    INDICE_EMPLEABILIDAD_RANKING_SUCCESS_MESSAGE,
    INDICE_EMPLEABILIDAD_ROUTE,
    OPENAPI_TAG_INDICE_EMPLEABILIDAD,
    NivelEmpleabilidad,
    OrdenRanking,
    PaisCodigo,
    TipoIndicador,
    normalizar_pais_codigo,
)
from app.domain.exceptions.base import DomainException

indice_empleabilidad_router = APIRouter(
    prefix=INDICE_EMPLEABILIDAD_ROUTE,
    tags=[OPENAPI_TAG_INDICE_EMPLEABILIDAD],
)


@indice_empleabilidad_router.get(
    INDICE_EMPLEABILIDAD_RANKING_ROUTE,
    response_model=IndiceRankingResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Ranking tabular de ocupaciones por Índice de Empleabilidad",
    description=(
        "Retorna el listado de ocupaciones con puestos disponibles y score de "
        "empleabilidad para comparativas multi-país."
    ),
)
async def get_ranking_ocupaciones(
    service: Annotated[
        IndiceEmpleabilidadService,
        Depends(provide_indice_empleabilidad_service),
    ],
    pais: Annotated[
        str | None, Query(description="Códigos ISO-3 en CSV (ej. 'ARG,URY,CHL')")
    ] = None,
    sector: Annotated[
        str | None, Query(description="Filtro opcional de sector")
    ] = None,
    periodo: Annotated[str | None, Query(description="Período temporal")] = None,
    orden: Annotated[
        OrdenRanking,
        Query(description="Criterio de ordenamiento ('score' o 'puestos')"),
    ] = OrdenRanking.SCORE,
) -> IndiceRankingResponseSchema:
    """Procesa el ranking de ocupaciones para la tabla de la vista Ocupaciones.

    Args:
        service: Servicio de aplicación para cálculo y ordenamiento del índice.
        pais: Códigos ISO 3166-1 alpha-3 separados por coma.
        sector: Filtro opcional por sector estratégico.
        periodo: Período temporal de corte.
        orden: Criterio de ordenamiento ('score' o 'puestos').

    Returns:
        IndiceRankingResponseSchema: Envoltorio ApiResponse con la lista clasificada
            de ocupaciones con puestos demandados y score de empleabilidad.

    Raises:
        DomainException: Si algún código o nombre de país no es reconocido.
    """
    paises_lista: list[str] = []
    if pais:
        for p in pais.split(","):
            p_clean = p.strip()
            if not p_clean:
                continue
            p_code = normalizar_pais_codigo(p_clean)
            if not p_code:
                raise DomainException(
                    ERROR_MSG_PAIS_NO_RECONOCIDO_TEMPLATE.format(pais=p_clean)
                )
            if p_code.value not in paises_lista:
                paises_lista.append(p_code.value)

    if not paises_lista:
        paises_lista = [
            PaisCodigo.ARG.value,
            PaisCodigo.URY.value,
            PaisCodigo.CHL.value,
        ]

    dtos = await service.get_ranking_multi_pais(
        paises=paises_lista,
        sector=sector,
        periodo=periodo,
        orden=orden,
    )

    items = [
        OcupacionRankingItemDto(
            ocupacion_id=dto.ocupacion_id,
            nombre=dto.nombre,
            puestos_disponibles=dto.puestos_disponibles,
            indice_empleabilidad=dto.indice_empleabilidad,
            pais=dto.pais,
            fuente=dto.fuente,
        )
        for dto in dtos
    ]

    return create_success_response(
        data=IndiceRankingDataSchema(ocupaciones=items),
        message=INDICE_EMPLEABILIDAD_RANKING_SUCCESS_MESSAGE,
        meta=ResponseMeta(total=len(items)),
    )


@indice_empleabilidad_router.get(
    INDICE_EMPLEABILIDAD_OCUPACION_ROUTE,
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
        nivel=NivelEmpleabilidad(dto.nivel),
        dimensiones=[
            DimensionIndiceSchema(
                nombre=dim.nombre,
                valor=dim.valor,
                peso=dim.peso,
                descripcion=dim.descripcion,
            )
            for dim in dto.dimensiones
        ],
        tipo=TipoIndicador(dto.tipo),
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
        message=INDICE_EMPLEABILIDAD_GET_SUCCESS_MESSAGE,
        status_code=status.HTTP_200_OK,
        meta=meta,
    )
