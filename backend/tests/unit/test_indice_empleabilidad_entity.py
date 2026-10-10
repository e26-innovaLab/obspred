"""Pruebas unitarias para las entidades y reglas del dominio de IndiceEmpleabilidad."""

import pytest

from app.domain.entities.indice_empleabilidad import (
    DimensionIndice,
    EvolucionIndicePunto,
    IndiceEmpleabilidad,
)


def test_dimension_indice_initialization_valid() -> None:
    """Verifica la correcta inicialización de una dimensión válida."""
    dim = DimensionIndice(
        nombre="Demanda de puestos",
        valor=85.5,
        peso=0.35,
        descripcion="Puestos vacantes analizados",
    )
    assert dim.nombre == "Demanda de puestos"
    assert dim.valor == 85.5
    assert dim.peso == 0.35
    assert dim.descripcion == "Puestos vacantes analizados"


def test_dimension_indice_invalid_valor() -> None:
    """Verifica que un valor fuera de [0, 100] lance ValueError."""
    with pytest.raises(ValueError, match="debe situarse entre 0 y 100"):
        DimensionIndice(nombre="Demanda", valor=105.0, peso=0.35)

    with pytest.raises(ValueError, match="debe situarse entre 0 y 100"):
        DimensionIndice(nombre="Demanda", valor=-1.0, peso=0.35)


def test_dimension_indice_invalid_peso() -> None:
    """Verifica que un peso fuera de [0, 1] lance ValueError."""
    with pytest.raises(ValueError, match="debe estar entre 0.0 y 1.0"):
        DimensionIndice(nombre="Demanda", valor=50.0, peso=1.5)

    with pytest.raises(ValueError, match="debe estar entre 0.0 y 1.0"):
        DimensionIndice(nombre="Demanda", valor=50.0, peso=-0.1)


def test_dimension_indice_empty_nombre() -> None:
    """Verifica que un nombre vacío lance ValueError."""
    with pytest.raises(ValueError, match="no puede estar vacío"):
        DimensionIndice(nombre="  ", valor=50.0, peso=0.3)


def test_evolucion_indice_punto_valid() -> None:
    """Verifica la inicialización de un punto temporal de evolución."""
    punto = EvolucionIndicePunto(periodo="2025-Q3", valor=77.2)
    assert punto.periodo == "2025-Q3"
    assert punto.valor == 77.2


def test_evolucion_indice_punto_invalid() -> None:
    """Verifica validación de restricciones en puntos de evolución."""
    with pytest.raises(ValueError, match="no puede estar vacío"):
        EvolucionIndicePunto(periodo=" ", valor=70.0)

    with pytest.raises(ValueError, match="debe situarse entre 0.0 y 100.0"):
        EvolucionIndicePunto(periodo="2025-Q1", valor=110.0)


def test_calcular_score_ponderado() -> None:
    """Verifica el cálculo ponderado del score a partir de las dimensiones."""
    dimensiones = [
        DimensionIndice(nombre="Demanda", valor=90.0, peso=0.35),
        DimensionIndice(nombre="Estabilidad", valor=80.0, peso=0.25),
        DimensionIndice(nombre="Cobertura", valor=70.0, peso=0.20),
        DimensionIndice(nombre="Crecimiento", valor=80.0, peso=0.20),
    ]
    # (90*0.35 + 80*0.25 + 70*0.20 + 80*0.20) / 1.0 = 31.5 + 20.0 + 14.0 + 16.0 = 81.5
    score = IndiceEmpleabilidad.calcular_score_ponderado(dimensiones)
    assert score == 81.5


def test_calcular_score_ponderado_vacio() -> None:
    """Verifica que sin dimensiones el score ponderado sea 0.0."""
    assert IndiceEmpleabilidad.calcular_score_ponderado([]) == 0.0


def test_determinar_nivel() -> None:
    """Verifica las categorías cualitativas del score."""
    assert IndiceEmpleabilidad.determinar_nivel(85.0) == "Muy Alto"
    assert IndiceEmpleabilidad.determinar_nivel(80.0) == "Muy Alto"
    assert IndiceEmpleabilidad.determinar_nivel(75.0) == "Alto"
    assert IndiceEmpleabilidad.determinar_nivel(65.0) == "Alto"
    assert IndiceEmpleabilidad.determinar_nivel(55.0) == "Medio"
    assert IndiceEmpleabilidad.determinar_nivel(50.0) == "Medio"
    assert IndiceEmpleabilidad.determinar_nivel(49.9) == "Bajo"
    assert IndiceEmpleabilidad.determinar_nivel(20.0) == "Bajo"


def test_indice_empleabilidad_entity_invariants() -> None:
    """Verifica restricciones de entidad IndiceEmpleabilidad."""
    with pytest.raises(ValueError, match="El ID de la ocupación no puede estar vacío"):
        IndiceEmpleabilidad(
            ocupacion_id="  ",
            ocupacion_nombre="Test",
            score=70.0,
            nivel="Alto",
            dimensiones=[],
        )

    with pytest.raises(ValueError, match="El score global debe situarse"):
        IndiceEmpleabilidad(
            ocupacion_id="dev-software",
            ocupacion_nombre="Test",
            score=105.0,
            nivel="Muy Alto",
            dimensiones=[],
        )
