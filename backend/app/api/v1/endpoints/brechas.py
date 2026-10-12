from typing import Optional
from fastapi import APIRouter, Path, Query, status

from app.api.v1.schemas.brechas_schema import (
    BrechasResponse,
    HabilidadBrechaItem,
    MetadatosFuente,
)
from app.core.constants import BRECHAS_ROUTE

brechas_router = APIRouter(
    prefix=BRECHAS_ROUTE,
    tags=["Brechas de Habilidades"],
)


@brechas_router.get(
    "/{ocupacion}",
    response_model=BrechasResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar brechas de habilidades por ocupacion",
    description="Expone la comparación entre la demanda del mercado y la oferta formativa para una ocupación dada.",
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
    sector: Optional[str] = Query(
        None,
        description="Sector económico para acotar el análisis",
        examples=["Tecnología"],
    ),
) -> BrechasResponse:
    habilidades_mock = [
        HabilidadBrechaItem(
            nombre="Alfabetización digital",
            demanda=95.0,
            oferta=60.0,
            brecha=35.0,
            es_emergente=False,
        ),
        HabilidadBrechaItem(
            nombre="Trabajo en equipo remoto",
            demanda=92.0,
            oferta=28.0,
            brecha=64.0,
            es_emergente=True,
        ),
        HabilidadBrechaItem(
            nombre="Pensamiento analítico",
            demanda=90.0,
            oferta=40.0,
            brecha=50.0,
            es_emergente=False,
        ),
    ]

    metadatos = MetadatosFuente(
        fuente="SENCE SABE / ESCO",
        fecha_actualizacion="2026-09-30",
        metodologia="Taxonomía de referencia ESCO con demanda observada en avisos SABE.",
    )

    return BrechasResponse(
        pais=pais,
        sector=sector if sector else "Tecnología",
        ocupacion=ocupacion,
        habilidades=habilidades_mock,
        metadatos=metadatos,
    )