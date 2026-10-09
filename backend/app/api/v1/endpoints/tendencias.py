from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional

from app.api.v1.schemas.tendencia_schema import (
    TendenciasResponse,
    PuntoSerie,
    PuntoProyeccion,
    CambioSignificativo,
    MetadatosFuente
)

router = APIRouter(
    prefix= "/tendencias",
    tags = ["Tendencias"]
)

@router.get(
    "/",
    response_model=TendenciasResponse,
    summary="Obtener serie temporal, proyecciones y cambios significativos",
    description= "Retorna la evolucion histórica y proyectada para un pais, sector, ocupación e indicador dados."
)

async def get_tendencias(
    pais: str = Query(default="Argentina", descripcion="Nombre del país p código ISO"),
    sector:str = Query(default="Todos los sectores", decripcion="Sector de actividad económica"),
    ocupacion: str = Query(default="Todas las ocupaciones", descripcion="Categoria u ocupación laboral"),
    indicador: str = Query(default="puestos_demandados", descripcion="Tipo de indicadr a consultar")

)-> TendenciasResponse:
    """
    Acá vamos a conectar con la capa de servicio/repositories
    por ahora dejamos datos Mockeados
    """

    #Simulacion de respuesta mock, para que front pueda testear

    return TendenciasResponse(
        pais=pais,
        sector=sector,
        ocupacion=ocupacion,
        indicador=indicador,
        serie_historica=[
            PuntoSerie(periodo="T3 2023", valor=1620.0, es_destacado=False),
            PuntoSerie(periodo="T4 2023", valor=1750.0, es_destacado=True), # Suba 8%
            PuntoSerie(periodo="T1 2024", valor=1768.0, es_destacado=False),
            PuntoSerie(periodo="T2 2024", valor=1760.0, es_destacado=False),
            PuntoSerie(periodo="T3 2024", valor=1758.0, es_destacado=False),
            PuntoSerie(periodo="T4 2024", valor=1835.0, es_destacado=False),
            PuntoSerie(periodo="T1 2025", valor=1868.0, es_destacado=False),
            PuntoSerie(periodo="T2 2025", valor=1852.0, es_destacado=False),
            PuntoSerie(periodo="T3 2025", valor=1826.0, es_destacado=False),
            PuntoSerie(periodo="T4 2025", valor=1860.0, es_destacado=False),
            PuntoSerie(periodo="T1 2026", valor=1820.0, es_destacado=False),
            PuntoSerie(periodo="T2 2026", valor=1933.0, es_destacado=True), # Suba 6.2%
        ],
        cambios_significativos=[
            CambioSignificativo(
                periodo="T4 2023",
                titulo="Puestos demandados: suba de 8 %",
                descripcion="Variación respecto del período anterior (T3 2023).",
                tipo_alerta="warning"
            ),
            CambioSignificativo(
                periodo="T2 2026",
                titulo="Puestos demandados: suba de 6,2 %",
                descripcion="Variación respecto del período anterior (T1 2026).",
                tipo_alerta="warning"
            )
        ],
        proyeccion=[
            PuntoProyeccion(periodo="T2 2026", valor_estimado=1933.0, limite_inferior=1933.0, limite_superior=1933.0),
            PuntoProyeccion(periodo="T3 2026", valor_estimado=1925.0, limite_inferior=1880.0, limite_superior=1980.0),
            PuntoProyeccion(periodo="T4 2026", valor_estimado=1940.0, limite_inferior=1870.0, limite_superior=2020.0),
        ],
        metadatos_historico=MetadatosFuente(
            fuente="CEPALSTAT",
            fecha="24/7/2026"
        ),
        metadatos_proyeccion=MetadatosFuente(
            fuente="CEPALSTAT",
            fecha="24/7/2026",
            metodologia="Proyección orientativa (regresión lineal sobre la serie trimestral observada)."
        )


)