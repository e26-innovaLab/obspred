from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class HabilidadBrechaModel(Base):
    """Mapeo relacional de la tabla de brechas de habilidades del Observatorio.

    Representa la comparación entre la demanda del mercado y la oferta
    formativa para una ocupación específica.
    """

    __tablename__ = "habilidades_brechas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Identificador numérico autoincremental del registro",
    )
    ocupacion: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        doc="Ocupación analizada según taxonomía normalizada",
    )
    habilidad: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Nombre de la habilidad evaluada",
    )
    demanda: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Puntuación o porcentaje de demanda en el mercado",
    )
    oferta_formativa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Puntuación o porcentaje de cobertura en la oferta educativa",
    )
    emergente: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indica si se trata de una habilidad emergente",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Marca de tiempo UTC de inserción en el sistema",
    )
