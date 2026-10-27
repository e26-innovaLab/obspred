from fastapi import APIRouter, Path, Query, status

from app.api.v1.schemas.brechas_schema import (
    BrechasResponseSchema,
    HabilidadBrechaItem,
    MetadatosFuente,
)
from app.api.v1.schemas.response_schema import (
    create_success_response,
)
from app.core.constants import BRECHAS_ROUTE

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

    data = BrechasResponseSchema(
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
        meta=metadatos,
    )
