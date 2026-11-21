from dataclasses import dataclass


@dataclass(frozen=True)
class HabilidadComparada:
    """Entidad de dominio pura para la comparación de habilidades."""

    habilidad: str
    demanda: float
    oferta_formativa: float
    emergente: bool = False

    @property
    def brecha(self) -> float:
        """Regla de negocio: la brecha se calcula como
        la diferencia entre demanda y oferta.
        """
        return max(0.0, self.demanda - self.oferta_formativa)
