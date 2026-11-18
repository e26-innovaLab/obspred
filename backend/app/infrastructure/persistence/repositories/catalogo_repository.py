"""Implementación SQLAlchemy del repositorio para el catálogo maestro de taxonomías."""

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo_dto import (
    IndicadorCatalogoDTO,
    OcupacionCatalogoDTO,
    PaisCatalogoDTO,
    PeriodosRangoDTO,
    SectorCatalogoDTO,
)
from app.core.constants import IndicadorSlug, PaisCodigo, SectorEstrategico
from app.core.logging import logger
from app.domain.interfaces.catalogo_repository import ICatalogoRepository
from app.infrastructure.persistence.models.catalogo import (
    CatalogoIndicadorModel,
    CatalogoOcupacionModel,
    CatalogoPaisModel,
    CatalogoSectorModel,
)
from app.infrastructure.persistence.models.indicador import IndicadorModel

CANONICAL_PAISES: list[dict[str, Any]] = [
    {"id": PaisCodigo.ARG, "nombre": "Argentina", "orden": 1},
    {"id": PaisCodigo.URY, "nombre": "Uruguay", "orden": 2},
    {"id": PaisCodigo.CHL, "nombre": "Chile", "orden": 3},
]

CANONICAL_SECTORES: list[dict[str, Any]] = [
    {
        "id": SectorEstrategico.TECNOLOGIA,
        "nombre": "Tecnología",
        "isic": ["J"],
        "orden": 1,
    },
    {
        "id": SectorEstrategico.SALUD,
        "nombre": "Salud",
        "isic": ["Q"],
        "orden": 2,
    },
    {
        "id": SectorEstrategico.ENERGIA,
        "nombre": "Energía",
        "isic": ["D"],
        "orden": 3,
    },
    {
        "id": SectorEstrategico.TURISMO,
        "nombre": "Turismo",
        "isic": ["I"],
        "orden": 4,
    },
    {
        "id": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "nombre": "Economía del Conocimiento",
        "isic": ["M"],
        "orden": 5,
    },
]

CANONICAL_OCUPACIONES: list[dict[str, Any]] = [
    # Tecnología
    {
        "id": "dev-software",
        "nombre": "Desarrollador/a de software",
        "sector_id": SectorEstrategico.TECNOLOGIA,
        "isco": "2512",
        "orden": 1,
    },
    {
        "id": "analista-datos",
        "nombre": "Analista de datos",
        "sector_id": SectorEstrategico.TECNOLOGIA,
        "isco": "2511",
        "orden": 2,
    },
    {
        "id": "especialista-ciberseguridad",
        "nombre": "Especialista en ciberseguridad",
        "sector_id": SectorEstrategico.TECNOLOGIA,
        "isco": "2529",
        "orden": 3,
    },
    {
        "id": "devops",
        "nombre": "Ingeniero/a DevOps / Cloud",
        "sector_id": SectorEstrategico.TECNOLOGIA,
        "isco": "2519",
        "orden": 4,
    },
    # Salud
    {
        "id": "enfermeria",
        "nombre": "Enfermero/a profesional",
        "sector_id": SectorEstrategico.SALUD,
        "isco": "2221",
        "orden": 5,
    },
    {
        "id": "medico-general",
        "nombre": "Médico/a general",
        "sector_id": SectorEstrategico.SALUD,
        "isco": "2211",
        "orden": 6,
    },
    {
        "id": "tecnico-laboratorio",
        "nombre": "Técnico/a de laboratorio clínico",
        "sector_id": SectorEstrategico.SALUD,
        "isco": "3212",
        "orden": 7,
    },
    {
        "id": "kinesiologia",
        "nombre": "Kinesiólogo/a y fisioterapeuta",
        "sector_id": SectorEstrategico.SALUD,
        "isco": "2264",
        "orden": 8,
    },
    # Energía
    {
        "id": "ing-renovables",
        "nombre": "Ingeniero/a en energías renovables",
        "sector_id": SectorEstrategico.ENERGIA,
        "isco": "2149",
        "orden": 9,
    },
    {
        "id": "tecnico-solar",
        "nombre": "Técnico/a en instalaciones solares",
        "sector_id": SectorEstrategico.ENERGIA,
        "isco": "3113",
        "orden": 10,
    },
    {
        "id": "operador-redes",
        "nombre": "Operador/a de redes eléctricas",
        "sector_id": SectorEstrategico.ENERGIA,
        "isco": "3131",
        "orden": 11,
    },
    {
        "id": "gestor-ambiental",
        "nombre": "Especialista en eficiencia energética",
        "sector_id": SectorEstrategico.ENERGIA,
        "isco": "2143",
        "orden": 12,
    },
    # Turismo
    {
        "id": "guia-turismo",
        "nombre": "Guía de turismo especializado",
        "sector_id": SectorEstrategico.TURISMO,
        "isco": "5113",
        "orden": 13,
    },
    {
        "id": "gestor-hotelero",
        "nombre": "Gerente de servicios de alojamiento",
        "sector_id": SectorEstrategico.TURISMO,
        "isco": "1411",
        "orden": 14,
    },
    {
        "id": "chef-ejecutivo",
        "nombre": "Chef / Cocinero/a profesional",
        "sector_id": SectorEstrategico.TURISMO,
        "isco": "3434",
        "orden": 15,
    },
    {
        "id": "coordinador-eventos",
        "nombre": "Organizador/a de congresos y eventos",
        "sector_id": SectorEstrategico.TURISMO,
        "isco": "3332",
        "orden": 16,
    },
    # Economía del Conocimiento
    {
        "id": "product-manager",
        "nombre": "Gerente de producto digital",
        "sector_id": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "isco": "1219",
        "orden": 17,
    },
    {
        "id": "disenador-ux",
        "nombre": "Diseñador/a UX / UI",
        "sector_id": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "isco": "2166",
        "orden": 18,
    },
    {
        "id": "analista-financiero",
        "nombre": "Analista financiero y de inversiones",
        "sector_id": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "isco": "2412",
        "orden": 19,
    },
    {
        "id": "consultor-negocios",
        "nombre": "Consultor/a de innovación y estrategia",
        "sector_id": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "isco": "2421",
        "orden": 20,
    },
]

CANONICAL_INDICADORES: list[dict[str, Any]] = [
    {
        "id": IndicadorSlug.TASA_DESEMPLEO,
        "nombre": "Tasa de desempleo",
        "unidad": "%",
        "frecuencias": ["anual", "trimestral"],
        "desagregaciones": ["pais", "sector"],
        "descripcion": (
            "Porcentaje de la fuerza de trabajo desocupada que busca "
            "empleo activamente."
        ),
        "orden": 1,
    },
    {
        "id": IndicadorSlug.TASA_EMPLEO,
        "nombre": "Tasa de empleo",
        "unidad": "%",
        "frecuencias": ["anual", "trimestral"],
        "desagregaciones": ["pais", "sector"],
        "descripcion": (
            "Porcentaje de la población en edad de trabajar que se encuentra ocupada."
        ),
        "orden": 2,
    },
    {
        "id": IndicadorSlug.SALARIO_REAL_INDICE,
        "nombre": "Salario real (Índice)",
        "unidad": "pts",
        "frecuencias": ["trimestral", "mensual"],
        "desagregaciones": ["pais", "sector"],
        "descripcion": "Evolución del poder adquisitivo salarial ajustado.",
        "orden": 3,
    },
    {
        "id": IndicadorSlug.PUESTOS_DEMANDADOS,
        "nombre": "Puestos demandados",
        "unidad": "avisos",
        "frecuencias": ["trimestral", "mensual"],
        "desagregaciones": ["pais", "sector", "ocupacion"],
        "descripcion": ("Volumen de avisos de empleo y vacantes publicadas en bolsas."),
        "orden": 4,
    },
]


class SqlAlchemyCatalogoRepository(ICatalogoRepository):
    """Acceso y persistencia a tablas maestras de catálogo mediante SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_paises(self) -> list[PaisCatalogoDTO]:
        """Recupera países activos ordenados por prioridad."""
        query = (
            select(CatalogoPaisModel)
            .where(CatalogoPaisModel.activo.is_(True))
            .order_by(CatalogoPaisModel.orden, CatalogoPaisModel.id)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [PaisCatalogoDTO(id=m.id, nombre=m.nombre) for m in models]

    async def get_sectores(self) -> list[SectorCatalogoDTO]:
        """Recupera sectores productivos activos ordenados."""
        query = (
            select(CatalogoSectorModel)
            .where(CatalogoSectorModel.activo.is_(True))
            .order_by(CatalogoSectorModel.orden, CatalogoSectorModel.id)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [
            SectorCatalogoDTO(id=m.id, nombre=m.nombre, isic=m.isic or [])
            for m in models
        ]

    async def get_ocupaciones(
        self, sector_id: str | None = None
    ) -> list[OcupacionCatalogoDTO]:
        """Recupera ocupaciones normalizadas activas, con filtro opcional de sector."""
        query = (
            select(CatalogoOcupacionModel)
            .where(CatalogoOcupacionModel.activo.is_(True))
            .order_by(CatalogoOcupacionModel.orden, CatalogoOcupacionModel.id)
        )
        if sector_id:
            query = query.where(CatalogoOcupacionModel.sector_id == sector_id)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [
            OcupacionCatalogoDTO(
                id=m.id,
                nombre=m.nombre,
                sector=m.sector_id,
                isco=m.isco,
            )
            for m in models
        ]

    async def get_indicadores(self) -> list[IndicadorCatalogoDTO]:
        """Recupera definiciones maestras de indicadores habilitados."""
        query = (
            select(CatalogoIndicadorModel)
            .where(CatalogoIndicadorModel.activo.is_(True))
            .order_by(CatalogoIndicadorModel.orden, CatalogoIndicadorModel.id)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [
            IndicadorCatalogoDTO(
                id=m.id,
                nombre=m.nombre,
                unidad=m.unidad,
                frecuencias=m.frecuencias or [],
                desagregaciones=m.desagregaciones or [],
                descripcion=m.descripcion,
            )
            for m in models
        ]

    async def get_rango_periodos(self) -> PeriodosRangoDTO:
        """Calcula el rango cronológico min y max a partir de observaciones."""
        query = select(IndicadorModel.periodo, IndicadorModel.trimestre).distinct()
        result = await self._session.execute(query)
        raw_rows = result.all()

        parsed_entries: list[tuple[int, int, str]] = []

        for p_raw, q_raw in raw_rows:
            if not p_raw or p_raw.strip().lower() in ("actual", "null", "none"):
                continue

            clean_p = p_raw.strip()

            # Caso 1: fecha ISO 'YYYY-MM-DD'
            if re.match(r"^\d{4}-\d{2}-\d{2}", clean_p):
                year = int(clean_p[:4])
                month = int(clean_p[5:7])
                q_num = (month - 1) // 3 + 1
                rep = f"{year}-Q{q_num}"
                parsed_entries.append((year, q_num, rep))
                continue

            # Caso 2: período que contiene sufijo trimestral 'YYYY-QX' o 'YYYYQX'
            match_q_in_p = re.search(r"^(\d{4})[-_]?Q([1-4])$", clean_p, re.IGNORECASE)
            if match_q_in_p:
                year = int(match_q_in_p.group(1))
                q_num = int(match_q_in_p.group(2))
                rep = f"{year}-Q{q_num}"
                parsed_entries.append((year, q_num, rep))
                continue

            # Caso 3: año estándar de 4 dígitos con o sin columna trimestre
            match_year = re.match(r"^(\d{4})$", clean_p)
            if match_year:
                year = int(match_year.group(1))
                q_num = 0
                rep = str(year)
                if q_raw:
                    match_q = re.search(r"Q([1-4])", q_raw, re.IGNORECASE)
                    if match_q:
                        q_num = int(match_q.group(1))
                        rep = f"{year}-Q{q_num}"
                parsed_entries.append((year, q_num, rep))

        if not parsed_entries:
            return PeriodosRangoDTO(min=None, max=None)

        # Orden cronológico por (año, trimestre)
        parsed_entries.sort(key=lambda item: (item[0], item[1]))

        min_rep = parsed_entries[0][2]
        max_rep = parsed_entries[-1][2]

        return PeriodosRangoDTO(min=min_rep, max=max_rep)

    async def seed_catalogo_inicial(self) -> dict[str, int]:
        """Carga de forma idempotente las taxonomías maestras en la base de datos."""
        stats = {"paises": 0, "sectores": 0, "ocupaciones": 0, "indicadores": 0}

        # 1. Países
        for p in CANONICAL_PAISES:
            existing_p = await self._session.get(CatalogoPaisModel, p["id"])
            if not existing_p:
                self._session.add(CatalogoPaisModel(**p))
                stats["paises"] += 1

        # 2. Sectores
        for s in CANONICAL_SECTORES:
            existing_s = await self._session.get(CatalogoSectorModel, s["id"])
            if not existing_s:
                self._session.add(CatalogoSectorModel(**s))
                stats["sectores"] += 1

        await self._session.flush()

        # 3. Ocupaciones
        for o in CANONICAL_OCUPACIONES:
            existing_o = await self._session.get(CatalogoOcupacionModel, o["id"])
            if not existing_o:
                self._session.add(CatalogoOcupacionModel(**o))
                stats["ocupaciones"] += 1

        # 4. Indicadores
        for i in CANONICAL_INDICADORES:
            existing_i = await self._session.get(CatalogoIndicadorModel, i["id"])
            if not existing_i:
                self._session.add(CatalogoIndicadorModel(**i))
                stats["indicadores"] += 1

        await self._session.commit()
        logger.info(
            "Carga inicial de catálogo completada: %s",
            stats,
        )
        return stats
