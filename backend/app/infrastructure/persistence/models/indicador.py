"""Modelo de datos relacional para la entidad de Indicadores."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class IndicadorModel(Base):
    """Mapeo relacional de la tabla de indicadores socioeconómicos del Observatorio.

    Representa la serie temporal de un indicador específico desagregado por
    país, sector económico y ocupación con atributos completos de trazabilidad.
    """

    __tablename__ = "indicadores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Identificador numérico autoincremental del registro",
    )
    pais: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        doc="Identificador o código del país (ej. ARG, URY, CHL)",
    )
    sector: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Sector productivo o rama de actividad económica",
    )
    ocupacion: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
        doc="Ocupación analizada según taxonomía normalizada",
    )
    indicador: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Nombre o identificador clave del indicador (ej. tasa_desempleo)",
    )
    periodo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Período temporal del indicador (ej. 2024-Q1, 2024-01, 2024)",
    )
    valor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Valor numérico observado, calculado o proyectado",
    )
    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Tipo metodológico: observado, calculado o proyeccion",
    )
    fuente: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Organismo oficial o fuente de procedencia",
    )
    fecha_actualizacion: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Fecha de última actualización del indicador (YYYY-MM-DD)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Marca de tiempo UTC de inserción en el sistema",
    )

    __table_args__ = (
        Index(
            "ix_indicadores_pais_sector_ocupacion",
            "pais",
            "sector",
            "ocupacion",
        ),
        Index(
            "ix_indicadores_busqueda_temporal",
            "pais",
            "indicador",
            "periodo",
        ),
    )
