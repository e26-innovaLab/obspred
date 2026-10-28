from dataclasses import dataclass


@dataclass(frozen=True)
class HabilidadComparadaDTO:
    """DTO que transporta los datos de la habilidad comparada
    y su brecha hacia la API.
    """

    habilidad: str
    demanda: float
    oferta_formativa: float
    emergente: bool
    brecha: float


@dataclass(frozen=True)
class HabilidadComparadaCreateDTO:
    """DTO de entrada para registrar o actualizar habilidades de una ocupación."""

    habilidad: str
    demanda: float
    oferta_formativa: float
    emergente: bool = False
