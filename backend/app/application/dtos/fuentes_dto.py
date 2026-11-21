from dataclasses import dataclass
from datetime import datetime

from app.core.constants import FuenteEstado


@dataclass(frozen=True)
class FuenteDTO:
    id: int
    nombre: str
    descripcion: str | None
    url: str | None
    ultima_actualizacion: datetime | None
    estado: FuenteEstado
