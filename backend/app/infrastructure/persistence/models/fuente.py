from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import FuenteEstado
from app.infrastructure.persistence.database import Base


class FuenteModel(Base):
    """Mapeo relacional de la tabla de fuentes de datos del Observatorio.

    Representa la información de las fuentes de datos utilizadas para los indicadores
    socioeconómicos, laborales y educativos, incluyendo metadatos de trazabilidad.
    """

    __tablename__ = "fuentes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Identificador numérico autoincremental de la fuente",
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        doc="Nombre descriptivo de la fuente de datos",
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Descripción detallada de la fuente de datos",
    )
    url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="URL o enlace web asociado a la fuente de datos",
    )
    ultima_actualizacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha y hora de la última actualización registrada",
    )
    estado: Mapped[FuenteEstado] = mapped_column(
        SQLAlchemyEnum(
            FuenteEstado,
            name="fuente_estado",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=FuenteEstado.NO_DISPONIBLE,
    )
