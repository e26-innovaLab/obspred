from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from app.core.constants import FuenteEstado

@dataclass(frozen=True)
class Fuente:
    nombre: str
    descripcion: Optional[str] = None
    estado: FuenteEstado = FuenteEstado.NO_DISPONIBLE
    id: Optional[int] = None
    descripcion: Optional[str] = None
    url: Optional[str] = None
    ulima_actualizacion: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valida invariantes de la fuente tras inicializarse.

        Raises:
            ValueError: Si algún valor no cumple las restricciones.
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la fuente no puede estar vacío.")
        if self.estado not in FuenteEstado:
            raise ValueError(f"Estado '{self.estado}' no es válido para una fuente.")