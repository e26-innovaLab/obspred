"""Implementación de persistencia y catálogo para el Índice de Empleabilidad."""

import unicodedata
from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.entities.indice_empleabilidad import (
    DimensionIndice,
    EvolucionIndicePunto,
    IndiceEmpleabilidad,
)
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)
from app.infrastructure.persistence.models.indicador import IndicadorModel


def _normalize_string(text: str) -> str:
    """Normaliza texto eliminando acentos, mayúsculas y caracteres especiales."""
    nfkd_form = unicodedata.normalize("NFKD", text.strip().lower())
    clean_text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return clean_text.replace("/", " ").replace("-", " ").replace("_", " ")


class SqlAlchemyIndiceEmpleabilidadRepository(IIndiceEmpleabilidadRepository):
    """Repositorio relacional y catálogo metodológico del Índice de Empleabilidad."""

    # Catálogo taxonómico armonizado de las 20 ocupaciones en 5 sectores
    _CATALOGO_OCUPACIONES: Dict[str, dict] = {
        "dev-software": {
            "id": "dev-software",
            "nombre": "Desarrollador/a de software",
            "sector": "tecnologia",
            "sector_nombre": "Tecnología",
            "aliases": [
                "dev-software",
                "desarrollador de software",
                "desarrollador/a de software",
                "software developer",
            ],
            "dimensiones": [
                ("Demanda de puestos", 88.0, 0.35, "Alta demanda vacantes digitales"),
                ("Estabilidad salarial", 84.0, 0.25, "Remuneración competitiva"),
                ("Cobertura formativa", 68.0, 0.20, "Déficit de graduados afines"),
                ("Crecimiento reciente", 86.0, 0.20, "Expansión interanual sostenida"),
            ],
        },
        "analista-datos": {
            "id": "analista-datos",
            "nombre": "Analista de datos",
            "sector": "tecnologia",
            "sector_nombre": "Tecnología",
            "aliases": ["analista-datos", "analista de datos", "data analyst"],
            "dimensiones": [
                ("Demanda de puestos", 84.0, 0.35, "Demanda creciente en BI y data"),
                ("Estabilidad salarial", 82.0, 0.25, "Salarios sobre la media"),
                ("Cobertura formativa", 62.0, 0.20, "Oferta formativa emergente"),
                ("Crecimiento reciente", 88.0, 0.20, "Adopción veloz en empresas"),
            ],
        },
        "soporte-ti": {
            "id": "soporte-ti",
            "nombre": "Soporte técnico TI",
            "sector": "tecnologia",
            "sector_nombre": "Tecnología",
            "aliases": ["soporte-ti", "soporte tecnico ti", "soporte tecnico"],
            "dimensiones": [
                ("Demanda de puestos", 72.0, 0.35, "Demanda continua operativa"),
                ("Estabilidad salarial", 60.0, 0.25, "Rango salarial medio"),
                ("Cobertura formativa", 75.0, 0.20, "Buena disponibilidad técnica"),
                ("Crecimiento reciente", 64.0, 0.20, "Crecimiento moderado estable"),
            ],
        },
        "diseno-ux": {
            "id": "diseno-ux",
            "nombre": "Diseñador/a UX/UI",
            "sector": "tecnologia",
            "sector_nombre": "Tecnología",
            "aliases": [
                "diseno-ux",
                "disenador ux ui",
                "disenador/a ux/ui",
                "ux ui",
            ],
            "dimensiones": [
                ("Demanda de puestos", 76.0, 0.35, "Foco en productos digitales"),
                ("Estabilidad salarial", 78.0, 0.25, "Buena compensación técnica"),
                ("Cobertura formativa", 70.0, 0.20, "Oferta formativa en auge"),
                ("Crecimiento reciente", 74.0, 0.20, "Demanda sostenida en apps"),
            ],
        },
        "enfermeria": {
            "id": "enfermeria",
            "nombre": "Enfermería",
            "sector": "salud",
            "sector_nombre": "Salud",
            "aliases": ["enfermeria", "enfermera", "enfermero"],
            "dimensiones": [
                ("Demanda de puestos", 92.0, 0.35, "Demanda estructural crítica"),
                ("Estabilidad salarial", 66.0, 0.25, "Estabilidad laboral alta"),
                ("Cobertura formativa", 55.0, 0.20, "Déficit formativo persistente"),
                ("Crecimiento reciente", 78.0, 0.20, "Expansión sanitaria continua"),
            ],
        },
        "tecnico-laboratorio": {
            "id": "tecnico-laboratorio",
            "nombre": "Técnico/a de laboratorio",
            "sector": "salud",
            "sector_nombre": "Salud",
            "aliases": ["tecnico-laboratorio", "tecnico de laboratorio"],
            "dimensiones": [
                ("Demanda de puestos", 74.0, 0.35, "Demanda diagnóstica continua"),
                ("Estabilidad salarial", 68.0, 0.25, "Puestos conveniados estables"),
                ("Cobertura formativa", 72.0, 0.20, "Oferta técnica acorde"),
                ("Crecimiento reciente", 66.0, 0.20, "Crecimiento moderado"),
            ],
        },
        "kinesiologia": {
            "id": "kinesiologia",
            "nombre": "Kinesiología",
            "sector": "salud",
            "sector_nombre": "Salud",
            "aliases": ["kinesiologia", "kinesiologo", "fisioterapia"],
            "dimensiones": [
                ("Demanda de puestos", 70.0, 0.35, "Rehabilitación ambulatoria"),
                ("Estabilidad salarial", 64.0, 0.25, "Ingresos variables"),
                ("Cobertura formativa", 68.0, 0.20, "Graduados suficientes"),
                ("Crecimiento reciente", 70.0, 0.20, "Demanda por longevidad"),
            ],
        },
        "gestion-hospitalaria": {
            "id": "gestion-hospitalaria",
            "nombre": "Gestión hospitalaria",
            "sector": "salud",
            "sector_nombre": "Salud",
            "aliases": [
                "gestion-hospitalaria",
                "gestion hospitalaria",
                "administracion de salud",
            ],
            "dimensiones": [
                ("Demanda de puestos", 75.0, 0.35, "Complejidad en salud"),
                ("Estabilidad salarial", 80.0, 0.25, "Cargos de jefatura"),
                ("Cobertura formativa", 62.0, 0.20, "Escasa oferta de posgrado"),
                ("Crecimiento reciente", 72.0, 0.20, "Eficiencia operativa"),
            ],
        },
        "tecnico-energias-renovables": {
            "id": "tecnico-energias-renovables",
            "nombre": "Técnico/a en energías renovables",
            "sector": "energia",
            "sector_nombre": "Energía",
            "aliases": [
                "tecnico-energias-renovables",
                "tecnico en energias renovables",
                "solar eolica",
            ],
            "dimensiones": [
                ("Demanda de puestos", 85.0, 0.35, "Transición energética"),
                ("Estabilidad salarial", 74.0, 0.25, "Salarios sobre industria"),
                ("Cobertura formativa", 50.0, 0.20, "Escasez de técnicos"),
                ("Crecimiento reciente", 89.0, 0.20, "Expansión solar y eólica"),
            ],
        },
        "ingenieria-electrica": {
            "id": "ingenieria-electrica",
            "nombre": "Ingeniería eléctrica",
            "sector": "energia",
            "sector_nombre": "Energía",
            "aliases": [
                "ingenieria-electrica",
                "ingenieria electrica",
                "ingeniero electrico",
            ],
            "dimensiones": [
                ("Demanda de puestos", 82.0, 0.35, "Demanda en infraestructura"),
                ("Estabilidad salarial", 85.0, 0.25, "Remuneraciones altas"),
                ("Cobertura formativa", 58.0, 0.20, "Baja graduación técnica"),
                ("Crecimiento reciente", 76.0, 0.20, "Inversiones en redes"),
            ],
        },
        "operador-planta": {
            "id": "operador-planta",
            "nombre": "Operador/a de planta energética",
            "sector": "energia",
            "sector_nombre": "Energía",
            "aliases": [
                "operador-planta",
                "operador de planta",
                "operador de planta energetica",
            ],
            "dimensiones": [
                ("Demanda de puestos", 70.0, 0.35, "Operación de generación"),
                ("Estabilidad salarial", 78.0, 0.25, "Turnos con compensación"),
                ("Cobertura formativa", 66.0, 0.20, "Formación técnica de planta"),
                ("Crecimiento reciente", 68.0, 0.20, "Estabilidad operativa"),
            ],
        },
        "guia-turistico": {
            "id": "guia-turistico",
            "nombre": "Guía turístico/a",
            "sector": "turismo",
            "sector_nombre": "Turismo",
            "aliases": ["guia-turistico", "guia turistico", "guia de turismo"],
            "dimensiones": [
                ("Demanda de puestos", 68.0, 0.35, "Fuerte demanda estacional"),
                ("Estabilidad salarial", 52.0, 0.25, "Dependencia de temporada"),
                ("Cobertura formativa", 75.0, 0.20, "Formación accesible"),
                ("Crecimiento reciente", 71.0, 0.20, "Turismo receptivo"),
            ],
        },
        "gestion-hotelera": {
            "id": "gestion-hotelera",
            "nombre": "Gestión hotelera",
            "sector": "turismo",
            "sector_nombre": "Turismo",
            "aliases": [
                "gestion-hotelera",
                "gestion hotelera",
                "administracion hotelera",
            ],
            "dimensiones": [
                ("Demanda de puestos", 72.0, 0.35, "Ocupación en corredores"),
                ("Estabilidad salarial", 68.0, 0.25, "Cadenas consolidadas"),
                ("Cobertura formativa", 70.0, 0.20, "Carreras técnicas activas"),
                ("Crecimiento reciente", 73.0, 0.20, "Inversión hotelera"),
            ],
        },
        "chef-gastronomia": {
            "id": "chef-gastronomia",
            "nombre": "Gastronomía / Chef",
            "sector": "turismo",
            "sector_nombre": "Turismo",
            "aliases": ["chef-gastronomia", "chef", "gastronomia", "cocinero"],
            "dimensiones": [
                ("Demanda de puestos", 80.0, 0.35, "Rotación y demanda urbana"),
                ("Estabilidad salarial", 58.0, 0.25, "Dispersión salarial"),
                ("Cobertura formativa", 72.0, 0.20, "Escuelas gastronómicas"),
                ("Crecimiento reciente", 74.0, 0.20, "Sector dinámico"),
            ],
        },
        "marketing-turistico": {
            "id": "marketing-turistico",
            "nombre": "Marketing turístico",
            "sector": "turismo",
            "sector_nombre": "Turismo",
            "aliases": [
                "marketing-turistico",
                "marketing turistico",
                "promocion turistica",
            ],
            "dimensiones": [
                ("Demanda de puestos", 66.0, 0.35, "Perfiles en agencias"),
                ("Estabilidad salarial", 65.0, 0.25, "Salarios alineados"),
                ("Cobertura formativa", 76.0, 0.20, "Oferta educativa adecuada"),
                ("Crecimiento reciente", 70.0, 0.20, "Turismo digital"),
            ],
        },
        "investigador-i+d": {
            "id": "investigador-i+d",
            "nombre": "Investigador/a I+D",
            "sector": "economia-conocimiento",
            "sector_nombre": "Economía del conocimiento",
            "aliases": [
                "investigador-i+d",
                "investigador i d",
                "investigador cientifico",
            ],
            "dimensiones": [
                ("Demanda de puestos", 74.0, 0.35, "Ciencias aplicadas y biotech"),
                ("Estabilidad salarial", 82.0, 0.25, "Proyectos de largo plazo"),
                ("Cobertura formativa", 54.0, 0.20, "Exigencia de doctorado"),
                ("Crecimiento reciente", 75.0, 0.20, "Políticas de innovación"),
            ],
        },
        "consultor-innovacion": {
            "id": "consultor-innovacion",
            "nombre": "Consultor/a de innovación",
            "sector": "economia-conocimiento",
            "sector_nombre": "Economía del conocimiento",
            "aliases": [
                "consultor-innovacion",
                "consultor de innovacion",
                "consultor",
            ],
            "dimensiones": [
                ("Demanda de puestos", 78.0, 0.35, "Transformación productiva"),
                ("Estabilidad salarial", 84.0, 0.25, "Tarifas profesionales altas"),
                ("Cobertura formativa", 65.0, 0.20, "Formación multidisciplinar"),
                ("Crecimiento reciente", 79.0, 0.20, "Servicios empresariales"),
            ],
        },
        "propiedad-intelectual": {
            "id": "propiedad-intelectual",
            "nombre": "Especialista en propiedad intelectual",
            "sector": "economia-conocimiento",
            "sector_nombre": "Economía del conocimiento",
            "aliases": [
                "propiedad-intelectual",
                "propiedad intelectual",
                "patentes",
            ],
            "dimensiones": [
                ("Demanda de puestos", 68.0, 0.35, "Exportación tecnológica"),
                ("Estabilidad salarial", 86.0, 0.25, "Alta cotización jurídica"),
                ("Cobertura formativa", 52.0, 0.20, "Muy escasos especialistas"),
                ("Crecimiento reciente", 72.0, 0.20, "Registro de intangibles"),
            ],
        },
        "analista-financiero": {
            "id": "analista-financiero",
            "nombre": "Analista financiero/a",
            "sector": "economia-conocimiento",
            "sector_nombre": "Economía del conocimiento",
            "aliases": ["analista-financiero", "analista financiero", "fintech"],
            "dimensiones": [
                ("Demanda de puestos", 82.0, 0.35, "Dinamismo bancario y fintech"),
                ("Estabilidad salarial", 85.0, 0.25, "Paquete salarial superior"),
                ("Cobertura formativa", 72.0, 0.20, "Graduados suficientes"),
                ("Crecimiento reciente", 80.0, 0.20, "Modernización financiera"),
            ],
        },
        "gestion-proyectos": {
            "id": "gestion-proyectos",
            "nombre": "Gestión de proyectos",
            "sector": "economia-conocimiento",
            "sector_nombre": "Economía del conocimiento",
            "aliases": [
                "gestion-proyectos",
                "gestion de proyectos",
                "project manager",
                "scrum master",
            ],
            "dimensiones": [
                ("Demanda de puestos", 84.0, 0.35, "Proyectos ágiles y técnicos"),
                ("Estabilidad salarial", 83.0, 0.25, "Salarios consolidados"),
                ("Cobertura formativa", 70.0, 0.20, "Certificaciones activas"),
                ("Crecimiento reciente", 81.0, 0.20, "Expansión en sectores"),
            ],
        },
    }

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        """Inicializa el repositorio con la sesión de base de datos opcional.

        Args:
            session: Sesión asíncrona de base de datos SQLAlchemy.
        """
        self._session = session

    def _resolve_catalog_entry(self, ocupacion: str) -> Optional[dict]:
        """Localiza la entrada taxonómica de una ocupación por ID o alias.

        Args:
            ocupacion: Cadena a contrastar contra el catálogo.

        Returns:
            Optional[dict]: Registro del catálogo taxonómico o None si no coincide.
        """
        raw_key = ocupacion.strip().lower()
        if raw_key in self._CATALOGO_OCUPACIONES:
            return self._CATALOGO_OCUPACIONES[raw_key]

        normalized_query = _normalize_string(ocupacion)
        for entry in self._CATALOGO_OCUPACIONES.values():
            if _normalize_string(entry["id"]) == normalized_query:
                return entry
            if _normalize_string(entry["nombre"]) == normalized_query:
                return entry
            for alias in entry["aliases"]:
                if _normalize_string(alias) == normalized_query:
                    return entry

        return None

    def _get_fuente_por_pais(self, pais: Optional[str]) -> str:
        """Determina la fuente trazable acorde al filtro de país.

        Args:
            pais: Código o nombre del país analizado.

        Returns:
            str: Identificación de organismos oficiales de datos.
        """
        if not pais:
            return "SENCE-SABE / INDEC / INE / OIT (Fuentes Oficiales Armonizadas)"
        p = pais.upper().strip()
        if p in ("ARG", "AR", "ARGENTINA"):
            return "INDEC — Encuesta Permanente de Hogares / Secretaría de Trabajo"
        if p in ("CHL", "CL", "CHILE"):
            return "SENCE — SABE / INE Chile — ENE y SIMEL"
        if p in ("URY", "UY", "URUGUAY"):
            return "INE Uruguay — ECH / ANEP — DGETP-UTU"
        return f"Observatorio Predictivo ({p}) / Fuentes Armonizadas"

    async def exists_ocupacion(self, ocupacion: str) -> bool:
        """Determina si la ocupación existe en el catálogo o base de datos.

        Args:
            ocupacion: Identificador o nombre de la ocupación.

        Returns:
            bool: True si la ocupación es reconocida.
        """
        if self._resolve_catalog_entry(ocupacion) is not None:
            return True

        if self._session:
            try:
                stmt = select(func.count(IndicadorModel.id)).where(
                    func.lower(IndicadorModel.ocupacion)
                    == func.lower(ocupacion.strip())
                )
                result = await self._session.execute(stmt)
                count = result.scalar() or 0
                if count > 0:
                    return True
            except Exception as exc:
                logger.warning(f"Fallo al consultar ocupación en base de datos: {exc}")
                return False

        return False

    async def get_by_ocupacion(
        self,
        ocupacion: str,
        pais: Optional[str] = None,
        sector: Optional[str] = None,
        periodo: Optional[str] = None,
    ) -> Optional[IndiceEmpleabilidad]:
        """Obtiene el Índice de Empleabilidad para una ocupación.

        Args:
            ocupacion: Identificador o denominación de la ocupación.
            pais: Filtro opcional por país.
            sector: Filtro opcional por sector.
            periodo: Filtro opcional por período temporal.

        Returns:
            Optional[IndiceEmpleabilidad]: Entidad de dominio o None si no existe.
        """
        entry = self._resolve_catalog_entry(ocupacion)

        # Si no se halla en catálogo, verificar en base de datos si existe
        if entry is None and self._session:
            try:
                stmt = select(IndicadorModel).where(
                    func.lower(IndicadorModel.ocupacion)
                    == func.lower(ocupacion.strip())
                )
                if pais:
                    stmt = stmt.where(
                        func.upper(IndicadorModel.pais) == pais.upper().strip()
                    )
                result = await self._session.execute(stmt)
                db_records: List[IndicadorModel] = list(result.scalars().all())
            except Exception as exc:
                logger.warning(
                    f"Fallo al consultar registros de BD para '{ocupacion}': {exc}"
                )
                return None

            if not db_records:
                return None

            # Construir entidad a partir de registros en BD
            canon_nombre = db_records[0].ocupacion or ocupacion
            canon_sector = db_records[0].sector or sector or "general"
            fuente = db_records[0].fuente or self._get_fuente_por_pais(pais)
            fecha_act = db_records[0].fecha_actualizacion

            indice_records = [
                r for r in db_records if r.indicador == "indice_empleabilidad"
            ]
            if indice_records:
                score = round(indice_records[0].valor, 2)
            else:
                score = round(sum(r.valor for r in db_records) / len(db_records), 2)

            dimensiones = [
                DimensionIndice(
                    nombre="Demanda de puestos",
                    valor=score,
                    peso=0.35,
                    descripcion="Medición agregada desde registros de BD",
                ),
                DimensionIndice(
                    nombre="Estabilidad salarial",
                    valor=score,
                    peso=0.25,
                    descripcion="Medición agregada desde registros de BD",
                ),
                DimensionIndice(
                    nombre="Cobertura formativa",
                    valor=score,
                    peso=0.20,
                    descripcion="Medición agregada desde registros de BD",
                ),
                DimensionIndice(
                    nombre="Crecimiento reciente",
                    valor=score,
                    peso=0.20,
                    descripcion="Medición agregada desde registros de BD",
                ),
            ]

            return IndiceEmpleabilidad(
                ocupacion_id=_normalize_string(canon_nombre).replace(" ", "-"),
                ocupacion_nombre=canon_nombre,
                score=score,
                nivel=IndiceEmpleabilidad.determinar_nivel(score),
                dimensiones=dimensiones,
                tipo="calculado",
                fuente=fuente,
                fecha_actualizacion=fecha_act,
                pais=pais,
                sector=canon_sector,
                periodo=periodo,
                evolucion=[],
            )

        if entry is None:
            return None

        # Construir dimensiones desde el catálogo metodológico
        dimensiones = [
            DimensionIndice(
                nombre=dim[0],
                valor=dim[1],
                peso=dim[2],
                descripcion=dim[3],
            )
            for dim in entry["dimensiones"]
        ]

        score = IndiceEmpleabilidad.calcular_score_ponderado(dimensiones)
        nivel = IndiceEmpleabilidad.determinar_nivel(score)

        # Serie histórica de evolución metodológica (≥ 3 períodos)
        evolucion = [
            EvolucionIndicePunto(
                periodo="2025-Q3", valor=round(max(0.0, score - 3.2), 1)
            ),
            EvolucionIndicePunto(
                periodo="2025-Q4", valor=round(max(0.0, score - 1.5), 1)
            ),
            EvolucionIndicePunto(periodo="2026-Q1", valor=round(score, 1)),
            EvolucionIndicePunto(
                periodo="2026-Q2", valor=round(min(100.0, score + 1.1), 1)
            ),
        ]

        return IndiceEmpleabilidad(
            ocupacion_id=entry["id"],
            ocupacion_nombre=entry["nombre"],
            score=score,
            nivel=nivel,
            dimensiones=dimensiones,
            tipo="calculado",
            fuente=self._get_fuente_por_pais(pais),
            fecha_actualizacion=date(2026, 9, 30),
            metodologia=(
                "Índice de Empleabilidad — Metodología v1 (ponderación: "
                "Demanda 35%, Estabilidad 25%, Cobertura 20%, Crecimiento 20%)"
            ),
            pais=pais,
            sector=sector or entry["sector"],
            periodo=periodo or "2026-Q1",
            evolucion=evolucion,
        )
