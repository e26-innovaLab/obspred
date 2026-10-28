from typing import Annotated
"""Controlador y endpoints para el análisis de brechas formativas y de habilidades."""

from fastapi import APIRouter, Path, Query, status

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import provide_brecha_service
from app.api.v1.schemas.brechas_schema import (
    BrechasDataSchema,
    BrechasResponseSchema,
    HabilidadBrechaItem,
    MetadatosFuente,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.application.services.brecha_service import BrechaService
from app.core.constants import BRECHAS_ROUTE
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError
from app.core.constants import BRECHAS_ROUTE, OPENAPI_TAG_BRECHAS

brechas_router = APIRouter(
    prefix=BRECHAS_ROUTE,
    tags=[OPENAPI_TAG_BRECHAS],
)


@brechas_router.get(
    "",
    response_model=BrechasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar brechas de habilidades por sector",
    description="Expone la demanda y oferta formativa por sector.",
)
async def get_brechas_generales(
    pais: str = Query(
        "ARG",
        description="Código ISO del país (ARG, URY, CHL)",
        examples=["ARG"],
    ),
    sector: str | None = Query(
        None,
        description="Sector económico para acotar el análisis",
        examples=["Tecnología"],
    ),
) -> BrechasResponseSchema:
    """Procesa la consulta general de brechas de habilidades.

    Args:
        pais: Código ISO 3166-1 alpha-3 del país.
        sector: Filtro opcional por sector económico.

    Returns:
        BrechasResponseSchema: Envoltorio ApiResponse con las habilidades comparadas.
    """
    # TODO [backend]: Conectar con BrechasService / Repositorio de educación y vacantes:
    # 1. Inyectar servicio de brechas formativas.
    # 2. Integrar vacantes con matrículas y egresados educativos.
    # 3. Retornar cálculo de demanda vs oferta por competencia.
    return await get_brechas_por_ocupacion(
        ocupacion="general",
        pais=pais,
        sector=sector,
    )


@brechas_router.get(
    "/{ocupacion}",
    response_model=BrechasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar brechas de habilidades por ocupación",
    description=(
        "Expone la comparación entre la demanda del mercado y "
        "la oferta formativa para una ocupación dada."
    ),
)
async def get_brechas_por_ocupacion(
    ocupacion: Annotated[
        str,
        Path(
            ...,
            description="Identificador o nombre normalizado de la ocupación",
            examples=["desarrollador_software"],
        ),
    ],
    service: Annotated[
        BrechaService,
        Depends(provide_brecha_service),
    ],
    pais: Annotated[
        str,
        Query(
            description="Código ISO del país (ARG, URY, CHL)",
            examples=["ARG"],
        ),
    ] = "ARG",
    sector: Annotated[
        str | None,
        Query(
            description="Sector económico para acotar el análisis",
            examples=["Tecnología"],
        ),
    ] = None,
) -> BrechasResponseSchema:
    try:
        # 1. Obtenemos las brechas (DTOs) desde el servicio de aplicación
        habilidades_dtos = await service.get_by_ocupation(ocupacion)

        # 2. Mapeamos los DTOs de dominio a los esquemas de Pydantic de la API
        habilidades_items = [
            HabilidadBrechaItem(
                habilidad=dto.habilidad,
                demanda=dto.demanda,
                oferta_formativa=dto.oferta_formativa,
                emergente=dto.emergente,
                brecha=dto.brecha,
            )
            for dto in habilidades_dtos
        ]

        # 3. Armamos los metadatos de la fuente
        metadatos = MetadatosFuente(
            fuente="SENCE SABE / ESCO",
            fecha_actualizacion="2026-09-30",
            metodologia=(
                "Taxonomía de referencia ESCO con demanda observada en avisos SABE."
            ),
        )

        # 4. Construimos el esquema con los ítems mapeados
        data = BrechasDataSchema(
            pais=pais,
            sector=sector if sector else "Tecnología",
            ocupacion=ocupacion,
            habilidades=habilidades_items,
            metadatos=metadatos,
        )

        # 5. Retornamos la respuesta estandarizada
        return create_success_response(
            data=data,
            message="Brechas de habilidades obtenidas con éxito.",
            status_code=status.HTTP_200_OK
        )

    except OcupacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
