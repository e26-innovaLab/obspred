from app.application.dtos.brecha_dto import (
    HabilidadComparadaCreateDTO,
    HabilidadComparadaDTO,
)
from app.domain.entities.brecha import HabilidadComparada
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError
from app.domain.interfaces.brecha_repository import IBrechaRepository

DEFAULT_BRECHAS_CATALOG: dict[str, list[dict]] = {
    "desarrollador_software": [
        {
            "habilidad": "Alfabetización digital",
            "demanda": 95.0,
            "oferta_formativa": 60.0,
            "emergente": False,
        },
        {
            "habilidad": "Trabajo en equipo remoto",
            "demanda": 92.0,
            "oferta_formativa": 28.0,
            "emergente": True,
        },
        {
            "habilidad": "Pensamiento analítico",
            "demanda": 90.0,
            "oferta_formativa": 40.0,
            "emergente": False,
        },
        {
            "habilidad": "Cloud computing",
            "demanda": 94.0,
            "oferta_formativa": 45.0,
            "emergente": True,
        },
        {
            "habilidad": "Ciberseguridad y DevOps",
            "demanda": 88.0,
            "oferta_formativa": 35.0,
            "emergente": False,
        },
    ],
    "analista_datos": [
        {
            "habilidad": "Modelado de datos y SQL",
            "demanda": 92.0,
            "oferta_formativa": 55.0,
            "emergente": False,
        },
        {
            "habilidad": "Visualización y BI",
            "demanda": 88.0,
            "oferta_formativa": 60.0,
            "emergente": False,
        },
        {
            "habilidad": "Machine Learning aplicado",
            "demanda": 85.0,
            "oferta_formativa": 30.0,
            "emergente": True,
        },
        {
            "habilidad": "Storytelling con datos",
            "demanda": 80.0,
            "oferta_formativa": 42.0,
            "emergente": False,
        },
    ],
    "soporte_ti": [
        {
            "habilidad": "Soporte de infraestructura",
            "demanda": 82.0,
            "oferta_formativa": 70.0,
            "emergente": False,
        },
        {
            "habilidad": "Helpdesk y atención remota",
            "demanda": 78.0,
            "oferta_formativa": 65.0,
            "emergente": False,
        },
        {
            "habilidad": "Diagnóstico de redes",
            "demanda": 75.0,
            "oferta_formativa": 50.0,
            "emergente": False,
        },
    ],
    "enfermero_profesional": [
        {
            "habilidad": "Atención primaria de la salud",
            "demanda": 94.0,
            "oferta_formativa": 75.0,
            "emergente": False,
        },
        {
            "habilidad": "Telemedicina y registro clínico digital",
            "demanda": 86.0,
            "oferta_formativa": 35.0,
            "emergente": True,
        },
        {
            "habilidad": "Cuidado geriátrico especializado",
            "demanda": 89.0,
            "oferta_formativa": 45.0,
            "emergente": False,
        },
    ],
    "tecnico_solar_fotovoltaico": [
        {
            "habilidad": "Instalación de paneles solares",
            "demanda": 91.0,
            "oferta_formativa": 40.0,
            "emergente": True,
        },
        {
            "habilidad": "Eficiencia energética e inversores",
            "demanda": 85.0,
            "oferta_formativa": 38.0,
            "emergente": False,
        },
        {
            "habilidad": "Normativa ambiental y seguridad",
            "demanda": 80.0,
            "oferta_formativa": 60.0,
            "emergente": False,
        },
    ],
}


class BrechaService:
    """Servicio de aplicación que orquesta la consulta y persistencia de brechas."""

    def __init__(self, repository: IBrechaRepository) -> None:
        """Inicializa el servicio inyectando el repositorio de brechas."""
        self._repository = repository

    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparadaDTO]:
        """Consulta las brechas de habilidades para una ocupación dada."""
        sanitized_ocupacion = ocupacion.strip() if ocupacion else ""
        if not sanitized_ocupacion:
            raise OcupacionNoEncontradaError("La ocupación no puede estar vacía.")

        # 1. Intentamos obtener las entidades de dominio persistidas
        entities = await self._repository.get_by_ocupation(sanitized_ocupacion)

        # 2. Si aún no existen en DB, comprobamos si pertenece
        # al catálogo base para auto-persistirlas
        if not entities:
            norm_key = sanitized_ocupacion.lower().replace("-", "_").replace(" ", "_")
            if norm_key in DEFAULT_BRECHAS_CATALOG:
                default_data = [
                    HabilidadComparada(
                        habilidad=item["habilidad"],
                        demanda=float(item["demanda"]),
                        oferta_formativa=float(item["oferta_formativa"]),
                        emergente=bool(item.get("emergente", False)),
                    )
                    for item in DEFAULT_BRECHAS_CATALOG[norm_key]
                ]
                entities = await self._repository.save_habilidades(
                    sanitized_ocupacion, default_data
                )

        if not entities:
            raise OcupacionNoEncontradaError(sanitized_ocupacion)

        # 3. Mapeamos de Entidad de Dominio a DTO de Aplicación
        return [
            HabilidadComparadaDTO(
                habilidad=entity.habilidad,
                demanda=entity.demanda,
                oferta_formativa=entity.oferta_formativa,
                emergente=entity.emergente,
                brecha=entity.brecha,
            )
            for entity in entities
        ]

    async def save_habilidades_por_ocupacion(
        self,
        ocupacion: str,
        habilidades: list[HabilidadComparadaCreateDTO],
    ) -> list[HabilidadComparadaDTO]:
        """Persiste un conjunto de habilidades para una ocupación dada.

        Args:
            ocupacion: Identificador o nombre de la ocupación.
            habilidades: Lista de DTOs con las habilidades a persistir.

        Returns:
            list[HabilidadComparadaDTO]: Lista de habilidades persistidas.
        """
        sanitized_ocupacion = ocupacion.strip() if ocupacion else ""
        if not sanitized_ocupacion:
            raise OcupacionNoEncontradaError("La ocupación no puede estar vacía.")

        domain_entities = [
            HabilidadComparada(
                habilidad=h.habilidad.strip(),
                demanda=h.demanda,
                oferta_formativa=h.oferta_formativa,
                emergente=h.emergente,
            )
            for h in habilidades
        ]

        saved_entities = await self._repository.save_habilidades(
            sanitized_ocupacion, domain_entities
        )

        return [
            HabilidadComparadaDTO(
                habilidad=e.habilidad,
                demanda=e.demanda,
                oferta_formativa=e.oferta_formativa,
                emergente=e.emergente,
                brecha=e.brecha,
            )
            for e in saved_entities
        ]

    async def seed_catalogo(self) -> int:
        """Siembra todas las ocupaciones del catálogo por defecto en la base de datos.

        Returns:
            int: Cantidad de ocupaciones persistidas.
        """
        count = 0
        for ocupacion, items in DEFAULT_BRECHAS_CATALOG.items():
            entities = [
                HabilidadComparada(
                    habilidad=item["habilidad"],
                    demanda=float(item["demanda"]),
                    oferta_formativa=float(item["oferta_formativa"]),
                    emergente=bool(item.get("emergente", False)),
                )
                for item in items
            ]
            await self._repository.save_habilidades(ocupacion, entities)
            count += 1
        return count
