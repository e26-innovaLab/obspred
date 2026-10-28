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
from app.core.constants import BRECHAS_ROUTE
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError

brechas_router = APIRouter(
    prefix=BRECHAS_ROUTE,
    tags=["Brechas de Habilidades"],
)


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
        # 1. Obtenemos las brechas desde el servicio de aplicación
        habilidades_dtos = await service.get_by_ocupation(ocupacion)

        # 2. Armamos los metadatos de la fuente
        metadatos = MetadatosFuente(
            fuente="SENCE SABE / ESCO",
            fecha_actualizacion="2026-09-30",
            metodologia=(
                "Taxonomía de referencia ESCO con demanda observada en avisos SABE."
            ),
        )

        # 3. Construimos el esquema con los datos reales devueltos por el servicio
        data = BrechasDataSchema(
            pais=pais,
            sector=sector if sector else "Tecnología",
            ocupacion=ocupacion,
            habilidades=habilidades_dtos,
            metadatos=metadatos,
        )

        # 4. Retornamos la respuesta estandarizada
        return create_success_response(
            data=data,
            message="Brechas de habilidades obtenidas con éxito.",
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
            fuente="SENCE SABE / ESCO (Persistido)",
            fecha_actualizacion="2026-10-27",
            metodologia=(
                "Taxonomía ESCO con demanda y oferta formativa "
                "persistida en base de datos."
            ),
        )

        data = BrechasDataSchema(
            pais=payload.pais,
            sector=payload.sector if payload.sector else "Tecnología",
            ocupacion=ocupacion,
            habilidades=habilidades_dtos,
            metadatos=metadatos,
        )

        return create_success_response(
            data=data,
            message="Brechas de habilidades persistidas con éxito.",
            status_code=status.HTTP_201_CREATED,
            meta=ResponseMeta(total=len(habilidades_dtos)),
        )

    except OcupacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
