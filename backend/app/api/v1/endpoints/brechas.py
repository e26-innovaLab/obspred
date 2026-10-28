from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import provide_brecha_service
from app.api.v1.schemas.brechas_schema import (
    BrechaGuardarPayloadSchema,
    BrechasDataSchema,
    BrechasResponseSchema,
    MetadatosFuente,
)
from app.api.v1.schemas.response_schema import (
    ResponseMeta,
    create_success_response,
)
from app.application.dtos.brecha_dto import HabilidadComparadaCreateDTO
from app.application.services.brecha_service import BrechaService
from app.core.constants import (
    BRECHAS_GET_SUCCESS_MESSAGE,
    BRECHAS_ROUTE,
    BRECHAS_SAVE_SUCCESS_MESSAGE,
    DEFAULT_BRECHAS_METODOLOGIA,
    DEFAULT_BRECHAS_METODOLOGIA_PERSISTIDA,
    DEFAULT_BRECHAS_SOURCE,
    OPENAPI_TAG_BRECHAS,
    PaisCodigo,
    SectorEstrategico,
)
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError

brechas_router = APIRouter(
    prefix=BRECHAS_ROUTE,
    tags=[OPENAPI_TAG_BRECHAS],
)


@brechas_router.get(
    "",
    response_model=BrechasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar brechas de habilidades generales o por sector",
    description=(
        "Expone las brechas de habilidades consolidadas o por sector económico "
        "para alimentar la vista general de brechas requerida por el frontend."
    ),
)
async def get_brechas_generales(
    service: Annotated[
        BrechaService,
        Depends(provide_brecha_service),
    ],
    pais: Annotated[
        str,
        Query(
            description="Código ISO del país (ARG, URY, CHL)",
            examples=[PaisCodigo.ARG.value],
        ),
    ] = PaisCodigo.ARG.value,
    sector: Annotated[
        str | None,
        Query(
            description="Sector económico para acotar el análisis",
            examples=[SectorEstrategico.TECNOLOGIA.value],
        ),
    ] = None,
    ocupacion: Annotated[
        str | None,
        Query(
            description="Ocupación opcional para acotar las habilidades",
            examples=["desarrollador_software"],
        ),
    ] = None,
) -> BrechasResponseSchema:
    try:
        target_ocupacion = service.resolve_ocupacion_for_sector(
            sector=sector, ocupacion=ocupacion
        )
        habilidades_dtos = await service.get_by_ocupation(target_ocupacion)

        metadatos = MetadatosFuente(
            fuente=DEFAULT_BRECHAS_SOURCE,
            fecha_actualizacion="2026-09-30",
            metodologia=DEFAULT_BRECHAS_METODOLOGIA,
        )

        data = BrechasDataSchema(
            pais=pais,
            sector=sector if sector else SectorEstrategico.TECNOLOGIA.value,
            ocupacion=target_ocupacion,
            habilidades=habilidades_dtos,
            metadatos=metadatos,
        )

        return create_success_response(
            data=data,
            message=BRECHAS_GET_SUCCESS_MESSAGE,
            status_code=status.HTTP_200_OK,
            meta=ResponseMeta(total=len(habilidades_dtos)),
        )

    except OcupacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@brechas_router.get(
    "/{ocupacion}",
    response_model=BrechasResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar brechas de habilidades por ocupacion",
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
            examples=[PaisCodigo.ARG.value],
        ),
    ] = PaisCodigo.ARG.value,
    sector: Annotated[
        str | None,
        Query(
            description="Sector económico para acotar el análisis",
            examples=[SectorEstrategico.TECNOLOGIA.value],
        ),
    ] = None,
) -> BrechasResponseSchema:
    try:
        # 1. Obtenemos las brechas desde el servicio de aplicación
        habilidades_dtos = await service.get_by_ocupation(ocupacion)

        # 2. Armamos los metadatos de la fuente
        metadatos = MetadatosFuente(
            fuente=DEFAULT_BRECHAS_SOURCE,
            fecha_actualizacion="2026-09-30",
            metodologia=DEFAULT_BRECHAS_METODOLOGIA,
        )

        # 3. Construimos el esquema con los datos reales devueltos por el servicio
        data = BrechasDataSchema(
            pais=pais,
            sector=sector if sector else SectorEstrategico.TECNOLOGIA.value,
            ocupacion=ocupacion,
            habilidades=habilidades_dtos,
            metadatos=metadatos,
        )

        # 4. Retornamos la respuesta estandarizada
        return create_success_response(
            data=data,
            message=BRECHAS_GET_SUCCESS_MESSAGE,
            status_code=status.HTTP_200_OK,
            meta=ResponseMeta(total=len(habilidades_dtos)),
        )

    except OcupacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@brechas_router.post(
    "/{ocupacion}",
    response_model=BrechasResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar o actualizar brechas de habilidades por ocupacion",
    description=(
        "Persiste un conjunto de habilidades con su demanda y "
        "oferta formativa para una ocupación en la base de datos."
    ),
)
async def guardar_brechas_por_ocupacion(
    ocupacion: Annotated[
        str,
        Path(
            ...,
            description="Identificador o nombre normalizado de la ocupación",
            examples=["desarrollador_software"],
        ),
    ],
    payload: BrechaGuardarPayloadSchema,
    service: Annotated[
        BrechaService,
        Depends(provide_brecha_service),
    ],
) -> BrechasResponseSchema:
    try:
        dtos_in = [
            HabilidadComparadaCreateDTO(
                habilidad=item.habilidad,
                demanda=item.demanda,
                oferta_formativa=item.oferta_formativa,
                emergente=item.emergente,
            )
            for item in payload.habilidades
        ]

        habilidades_dtos = await service.save_habilidades_por_ocupacion(
            ocupacion=ocupacion,
            habilidades=dtos_in,
        )

        metadatos = MetadatosFuente(
            fuente=f"{DEFAULT_BRECHAS_SOURCE} (Persistido)",
            fecha_actualizacion="2026-10-27",
            metodologia=DEFAULT_BRECHAS_METODOLOGIA_PERSISTIDA,
        )

        data = BrechasDataSchema(
            pais=payload.pais,
            sector=(
                payload.sector if payload.sector else SectorEstrategico.TECNOLOGIA.value
            ),
            ocupacion=ocupacion,
            habilidades=habilidades_dtos,
            metadatos=metadatos,
        )

        return create_success_response(
            data=data,
            message=BRECHAS_SAVE_SUCCESS_MESSAGE,
            status_code=status.HTTP_201_CREATED,
            meta=ResponseMeta(total=len(habilidades_dtos)),
        )

    except OcupacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
