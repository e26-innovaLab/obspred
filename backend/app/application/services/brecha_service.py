from app.application.dtos.brecha_dto import HabilidadComparadaDTO
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError
from app.domain.interfaces.brecha_repository import IBrechaRepository


class BrechaService:
    """Servicio de aplicación que orquesta la consulta de brechas de habilidades."""

    def __init__(self, repository: IBrechaRepository) -> None:
        """Inicializa el servicio inyectando el repositorio de brechas."""
        self._repository = repository

    async def get_by_ocupation(self, ocupacion: str) -> list[HabilidadComparadaDTO]:
        """Consulta las brechas de habilidades para una ocupación dada."""
        sanitized_ocupacion = ocupacion.strip() if ocupacion else ""
        if not sanitized_ocupacion:
            raise OcupacionNoEncontradaError("La ocupación no puede estar vacía.")
        # 1. Obtenemos las entidades de dominio desde el repositorio
        entities = await self._repository.get_by_ocupation(sanitized_ocupacion)

        if not entities:
            raise OcupacionNoEncontradaError(sanitized_ocupacion)

        # 2. Mapeamos de Entidad de Dominio a DTO de Aplicación

        return [
            HabilidadComparadaDTO(
                habilidad=entity.habilidad,
                demanda=entity.demanda,
                oferta_formativa=entity.oferta_formativa,
                emergente=entity.emergente,
                brecha=entity.brecha,  # Propiedad calculada en el dominio
            )
            for entity in entities
        ]
