"""Controlador y endpoint para el catálogo maestro de filtros y taxonomías."""

from fastapi import APIRouter, status

from app.api.v1.schemas.catalogo_schema import (
    CatalogoDataSchema,
    CatalogoResponseSchema,
    IndicadorCatalogoDto,
    OcupacionCatalogoDto,
    PaisCatalogoDto,
    PeriodosRangoDto,
    SectorCatalogoDto,
)
from app.api.v1.schemas.response_schema import create_success_response
from app.core.constants import CATALOGO_ROUTE, OPENAPI_TAG_CATALOGO

catalogo_router = APIRouter(
    prefix=CATALOGO_ROUTE,
    tags=[OPENAPI_TAG_CATALOGO],
)


@catalogo_router.get(
    "",
    response_model=CatalogoResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Catálogo de taxonomías y filtros globales",
    description=(
        "Retorna la lista de países, sectores, ocupaciones, indicadores y "
        "períodos disponibles."
    ),
)
async def get_catalogo() -> CatalogoResponseSchema:
    """Procesa la obtención del catálogo unificado para los filtros del frontend.

    # TODO (Backend):
    # 1. Conectar con tablas maestras o servicio de taxonomías.
    # 2. Consultar rango real de períodos con observaciones en DB (MIN/MAX).
    # 3. Retornar desagregaciones disponibles por indicador.
    """
    paises = [
        PaisCatalogoDto(id="ARG", nombre="Argentina"),
        PaisCatalogoDto(id="URY", nombre="Uruguay"),
        PaisCatalogoDto(id="CHL", nombre="Chile"),
    ]

    sectores = [
        SectorCatalogoDto(id="tecnologia", nombre="Tecnología", isic=["J"]),
        SectorCatalogoDto(id="salud", nombre="Salud", isic=["Q"]),
        SectorCatalogoDto(id="energia", nombre="Energía", isic=["D"]),
        SectorCatalogoDto(id="turismo", nombre="Turismo", isic=["I"]),
        SectorCatalogoDto(
            id="economia-conocimiento", nombre="Economía del Conocimiento", isic=["M"]
        ),
    ]

    ocupaciones = [
        # Tecnología
        OcupacionCatalogoDto(
            id="dev-software",
            nombre="Desarrollador/a de software",
            sector="tecnologia",
            isco="2512",
        ),
        OcupacionCatalogoDto(
            id="analista-datos",
            nombre="Analista de datos",
            sector="tecnologia",
            isco="2511",
        ),
        OcupacionCatalogoDto(
            id="especialista-ciberseguridad",
            nombre="Especialista en ciberseguridad",
            sector="tecnologia",
            isco="2529",
        ),
        OcupacionCatalogoDto(
            id="devops",
            nombre="Ingeniero/a DevOps / Cloud",
            sector="tecnologia",
            isco="2519",
        ),
        # Salud
        OcupacionCatalogoDto(
            id="enfermeria",
            nombre="Enfermero/a profesional",
            sector="salud",
            isco="2221",
        ),
        OcupacionCatalogoDto(
            id="medico-general", nombre="Médico/a general", sector="salud", isco="2211"
        ),
        OcupacionCatalogoDto(
            id="tecnico-laboratorio",
            nombre="Técnico/a de laboratorio clínico",
            sector="salud",
            isco="3212",
        ),
        OcupacionCatalogoDto(
            id="kinesiologia",
            nombre="Kinesiólogo/a y fisioterapeuta",
            sector="salud",
            isco="2264",
        ),
        # Energía
        OcupacionCatalogoDto(
            id="ing-renovables",
            nombre="Ingeniero/a en energías renovables",
            sector="energia",
            isco="2149",
        ),
        OcupacionCatalogoDto(
            id="tecnico-solar",
            nombre="Técnico/a en instalaciones solares",
            sector="energia",
            isco="3113",
        ),
        OcupacionCatalogoDto(
            id="operador-redes",
            nombre="Operador/a de redes eléctricas",
            sector="energia",
            isco="3131",
        ),
        OcupacionCatalogoDto(
            id="gestor-ambiental",
            nombre="Especialista en eficiencia energética",
            sector="energia",
            isco="2143",
        ),
        # Turismo
        OcupacionCatalogoDto(
            id="guia-turismo",
            nombre="Guía de turismo especializado",
            sector="turismo",
            isco="5113",
        ),
        OcupacionCatalogoDto(
            id="gestor-hotelero",
            nombre="Gerente de servicios de alojamiento",
            sector="turismo",
            isco="1411",
        ),
        OcupacionCatalogoDto(
            id="chef-ejecutivo",
            nombre="Chef / Cocinero/a profesional",
            sector="turismo",
            isco="3434",
        ),
        OcupacionCatalogoDto(
            id="coordinador-eventos",
            nombre="Organizador/a de congresos y eventos",
            sector="turismo",
            isco="3332",
        ),
        # Economía del Conocimiento
        OcupacionCatalogoDto(
            id="product-manager",
            nombre="Gerente de producto digital",
            sector="economia-conocimiento",
            isco="1219",
        ),
        OcupacionCatalogoDto(
            id="disenador-ux",
            nombre="Diseñador/a UX / UI",
            sector="economia-conocimiento",
            isco="2166",
        ),
        OcupacionCatalogoDto(
            id="analista-financiero",
            nombre="Analista financiero y de inversiones",
            sector="economia-conocimiento",
            isco="2412",
        ),
        OcupacionCatalogoDto(
            id="consultor-negocios",
            nombre="Consultor/a de innovación y estrategia",
            sector="economia-conocimiento",
            isco="2421",
        ),
    ]

    indicadores = [
        IndicadorCatalogoDto(
            id="tasa_desempleo",
            nombre="Tasa de desempleo",
            unidad="%",
            frecuencias=["anual", "trimestral"],
            desagregaciones=["pais", "sector"],
            descripcion=(
                "Porcentaje de la fuerza de trabajo desocupada que busca "
                "empleo activamente."
            ),
        ),
        IndicadorCatalogoDto(
            id="tasa_empleo",
            nombre="Tasa de empleo",
            unidad="%",
            frecuencias=["anual", "trimestral"],
            desagregaciones=["pais", "sector"],
            descripcion=(
                "Porcentaje de la población en edad de trabajar que se "
                "encuentra ocupada."
            ),
        ),
        IndicadorCatalogoDto(
            id="salario_real_indice",
            nombre="Salario real (Índice)",
            unidad="pts",
            frecuencias=["trimestral", "mensual"],
            desagregaciones=["pais", "sector"],
            descripcion="Evolución del poder adquisitivo salarial ajustado.",
        ),
        IndicadorCatalogoDto(
            id="puestos_demandados",
            nombre="Puestos demandados",
            unidad="avisos",
            frecuencias=["trimestral", "mensual"],
            desagregaciones=["pais", "sector", "ocupacion"],
            descripcion=(
                "Volumen de avisos de empleo y vacantes publicadas en bolsas."
            ),
        ),
    ]

    periodos = PeriodosRangoDto(min="2018-Q1", max="2026-Q2")

    data = CatalogoDataSchema(
        paises=paises,
        sectores=sectores,
        ocupaciones=ocupaciones,
        indicadores=indicadores,
        periodos=periodos,
    )

    return create_success_response(
        data=data,
        message="Catálogo de taxonomías recuperado con éxito.",
    )
