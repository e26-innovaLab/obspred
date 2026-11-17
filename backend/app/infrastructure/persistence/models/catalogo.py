"""Modelos relacionales SQLAlchemy para las tablas maestras del catálogo."""

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base


class CatalogoPaisModel(Base):
    """Mapeo relacional de países habilitados en el Observatorio."""

    __tablename__ = "catalogo_paises"

    id: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
        doc="Código ISO 3166-1 alpha-3 (ej. 'ARG', 'URY', 'CHL')",
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nombre oficial o display del país",
    )
    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Orden de presentación en interfaces de usuario",
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Indica si el país está activo para consultas y filtros",
    )


class CatalogoSectorModel(Base):
    """Mapeo relacional de sectores productivos y estratégicos."""

    __tablename__ = "catalogo_sectores"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Slug canónico del sector (ej. 'tecnologia', 'salud')",
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Denominación legible del sector",
    )
    isic: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Códigos de clasificación internacional ISIC/CIIU asociados",
    )
    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Orden de prioridad sectorial",
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Indica si el sector está disponible en los filtros",
    )

    ocupaciones: Mapped[list["CatalogoOcupacionModel"]] = relationship(
        "CatalogoOcupacionModel",
        back_populates="sector_rel",
        cascade="all, delete-orphan",
    )


class CatalogoOcupacionModel(Base):
    """Mapeo relacional de ocupaciones normalizadas vinculadas a un sector."""

    __tablename__ = "catalogo_ocupaciones"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Slug único de la ocupación (ej. 'dev-software')",
    )
    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Título profesional u ocupacional legible",
    )
    sector_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("catalogo_sectores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al sector estratégico al que pertenece",
    )
    isco: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Código ocupacional internacional ISCO-08",
    )
    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Orden relativo de visualización",
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Indica si la ocupación está disponible en filtros",
    )

    sector_rel: Mapped["CatalogoSectorModel"] = relationship(
        "CatalogoSectorModel",
        back_populates="ocupaciones",
    )


class CatalogoIndicadorModel(Base):
    """Mapeo relacional de definiciones maestras de indicadores."""

    __tablename__ = "catalogo_indicadores"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Slug identificador del indicador (ej. 'tasa_desempleo')",
    )
    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Nombre legible del indicador",
    )
    unidad: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Unidad de medida (ej. '%', 'pts', 'avisos')",
    )
    frecuencias: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Frecuencias válidas del indicador (anual, trimestral, mensual)",
    )
    desagregaciones: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Dimensiones aplicables: pais, sector, ocupacion",
    )
    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Nota conceptual o metodológica",
    )
    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Orden de despliegue",
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Indica si el indicador está habilitado en el catálogo",
    )
