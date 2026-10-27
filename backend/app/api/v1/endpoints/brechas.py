"""Controlador y endpoints para el análisis de brechas formativas y de habilidades."""

from fastapi import APIRouter, Path, Query, status

from app.api.v1.schemas.brechas_schema import (
    BrechasDataSchema,
    BrechasResponseSchema,
    HabilidadBrechaItem,
    MetadatosFuente,
)
from app.api.v1.schemas.response_schema import create_success_response
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

    # TODO (Backend):
    # 1. Inyectar servicio de brechas formativas.
    # 2. Integrar vacantes con matrículas y egresados educativos.
    # 3. Retornar cálculo de demanda vs oferta por competencia.
    """
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
    ocupacion: str = Path(
        ...,
        description="Identificador o nombre normalizado de la ocupación",
        examples=["desarrollador_software"],
    ),
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
    """Procesa la consulta de brechas para una ocupación específica.

    # TODO (Backend):
    # 1. Inyectar servicio de brechas formativas.
    # 2. Filtrar habilidades asociadas a la ocupación dada.
    """
    habilidades_mock = [
        HabilidadBrechaItem(
            habilidad="Alfabetización digital",
            demanda=95.0,
            ofertaFormativa=60.0,
            emergente=False,
        ),
        HabilidadBrechaItem(
            habilidad="Trabajo en equipo remoto",
            demanda=92.0,
            ofertaFormativa=28.0,
            emergente=True,
        ),
        HabilidadBrechaItem(
            habilidad="Pensamiento analítico",
            demanda=90.0,
            ofertaFormativa=40.0,
            emergente=False,
        ),
    ]

    metadatos = MetadatosFuente(
        fuente="SENCE SABE / ESCO",
        fecha_actualizacion="2026-09-30",
        metodologia=(
            "Taxonomía de referencia ESCO con demanda observada en avisos SABE."
        ),
    )

    data = BrechasDataSchema(
        pais=pais,
        sector=sector if sector else "Tecnología",
        ocupacion=ocupacion,
        habilidades=habilidades_mock,
        metadatos=metadatos,
    )
    return create_success_response(
        data=data,
        message="Brechas de habilidades obtenidas con éxito.",
        status_code=status.HTTP_200_OK,
    )
