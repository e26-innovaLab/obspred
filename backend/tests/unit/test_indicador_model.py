"""Pruebas unitarias para el modelo ORM IndicadorModel."""

from datetime import date

from app.infrastructure.persistence.models.indicador import IndicadorModel


def test_indicador_model_initialization() -> None:
    """Verifica que IndicadorModel instancie sus campos y atributos correctamente."""
    record = IndicadorModel(
        pais="ARG",
        sector="Tecnología",
        ocupacion="Desarrollador de software",
        indicador="tasa_desempleo",
        periodo="2024-Q1",
        valor=6.9,
        tipo="observado",
        fuente="ILOSTAT",
        fecha_actualizacion=date(2026, 9, 30),
    )

    assert record.__tablename__ == "indicadores"
    assert record.pais == "ARG"
    assert record.sector == "Tecnología"
    assert record.ocupacion == "Desarrollador de software"
    assert record.indicador == "tasa_desempleo"
    assert record.periodo == "2024-Q1"
    assert record.valor == 6.9
    assert record.tipo == "observado"
    assert record.fuente == "ILOSTAT"
    assert record.fecha_actualizacion == date(2026, 9, 30)
    assert record.updated_at is None


def test_indicador_model_indices_defined() -> None:
    """Verifica que los índices declarativos de búsqueda estén definidos en la tabla."""
    index_names = {idx.name for idx in IndicadorModel.__table__.indexes}

    assert "ix_indicadores_pais_sector_ocupacion" in index_names
    assert "ix_indicadores_busqueda_temporal" in index_names
