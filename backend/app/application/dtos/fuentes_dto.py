from datetime import datetime
from dataclasses import dataclass
from app.domain.enums.fuente_estado import FuenteEstado


@dataclass(frozen=True)
class FuenteDTO:
    id: int
    nombre: str
    descripcion: str | None
    url: str | None
    ultima_actualizacion: datetime | None
    estado: FuenteEstado
