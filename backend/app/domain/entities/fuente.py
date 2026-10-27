from dataclasses import dataclass
from datetime import datetime

from app.core.constants import FuenteEstado


@dataclass(frozen=True)
class Fuente:
    nombre: str
    descripcion: str | None = None
    estado: FuenteEstado = FuenteEstado.NO_DISPONIBLE
    id: int | None = None
    descripcion: str | None = None
    url: str | None = None
    ulima_actualizacion: datetime | None = None

    def __post_init__(self) -> None:
        """Valida invariantes de la fuente tras inicializarse.

        Raises:
            ValueError: Si algún valor no cumple las restricciones.
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la fuente no puede estar vacío.")
        if self.estado not in FuenteEstado:
            raise ValueError(f"Estado '{self.estado}' no es válido para una fuente.")
