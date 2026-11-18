"""Pruebas unitarias para el módulo central de constantes y normalizaciones."""

import pytest

from app.core.constants import (
    INDICE_EMPLEABILIDAD_PESOS_DEFAULT,
    AlertaNivel,
    AlertaTipo,
    DimensionIndiceNombre,
    FuenteEstado,
    IndicadorSlug,
    PaisCodigo,
    SectorEstrategico,
    TipoIndicador,
    normalizar_pais_codigo,
)


@pytest.mark.parametrize(
    ("input_pais", "expected"),
    [
        # Códigos ISO Alpha-2
        ("AR", PaisCodigo.ARG),
        ("ar", PaisCodigo.ARG),
        ("CL", PaisCodigo.CHL),
        ("cl", PaisCodigo.CHL),
        ("UY", PaisCodigo.URY),
        ("uy", PaisCodigo.URY),
        # Códigos ISO Alpha-3
        ("ARG", PaisCodigo.ARG),
        ("arg", PaisCodigo.ARG),
        ("CHL", PaisCodigo.CHL),
        ("chl", PaisCodigo.CHL),
        ("URY", PaisCodigo.URY),
        ("ury", PaisCodigo.URY),
        # Nombres completos
        ("Argentina", PaisCodigo.ARG),
        ("argentina", PaisCodigo.ARG),
        ("Chile", PaisCodigo.CHL),
        ("chile", PaisCodigo.CHL),
        ("Uruguay", PaisCodigo.URY),
        ("uruguay", PaisCodigo.URY),
        # Códigos numéricos M49
        ("032", PaisCodigo.ARG),
        ("152", PaisCodigo.CHL),
        ("858", PaisCodigo.URY),
        # Entradas con espacios / padding
        ("  cl  ", PaisCodigo.CHL),
        (" ARG ", PaisCodigo.ARG),
        (" Uruguay  ", PaisCodigo.URY),
        # Casos inválidos o vacíos
        (None, None),
        ("", None),
        ("   ", None),
        ("BR", None),
        ("Brasil", None),
        ("999", None),
        ("desconocido", None),
    ],
)
def test_normalizar_pais_codigo(input_pais: str | None, expected: str | None) -> None:
    """Verifica que normalizar_pais_codigo resuelva correctamente códigos válidos
    y retorne None ante entradas inválidas o nulas.
    """
    assert normalizar_pais_codigo(input_pais) == expected


def test_indice_empleabilidad_pesos_default_sum_one() -> None:
    """Verifica que la ponderación de las dimensiones del Índice de Empleabilidad
    sume exactamente 1.0 y contenga todas las dimensiones definidas.
    """
    dimensiones_esperadas = {
        DimensionIndiceNombre.DEMANDA_PUESTOS,
        DimensionIndiceNombre.ESTABILIDAD_SALARIAL,
        DimensionIndiceNombre.COBERTURA_FORMATIVA,
        DimensionIndiceNombre.CRECIMIENTO_RECIENTE,
    }

    assert set(INDICE_EMPLEABILIDAD_PESOS_DEFAULT.keys()) == dimensiones_esperadas
    assert sum(INDICE_EMPLEABILIDAD_PESOS_DEFAULT.values()) == pytest.approx(1.0)
    assert (
        INDICE_EMPLEABILIDAD_PESOS_DEFAULT[DimensionIndiceNombre.DEMANDA_PUESTOS]
        == 0.35
    )
    assert (
        INDICE_EMPLEABILIDAD_PESOS_DEFAULT[DimensionIndiceNombre.ESTABILIDAD_SALARIAL]
        == 0.25
    )
    assert (
        INDICE_EMPLEABILIDAD_PESOS_DEFAULT[DimensionIndiceNombre.COBERTURA_FORMATIVA]
        == 0.20
    )
    assert (
        INDICE_EMPLEABILIDAD_PESOS_DEFAULT[DimensionIndiceNombre.CRECIMIENTO_RECIENTE]
        == 0.20
    )


def test_enums_valores_y_unicidad() -> None:
    """Verifica consistencia y valores canónicos de los enums centrales."""
    # TipoIndicador
    assert TipoIndicador.OBSERVADO == "observado"
    assert TipoIndicador.CALCULADO == "calculado"
    assert TipoIndicador.PROYECCION == "proyeccion"

    # FuenteEstado
    assert FuenteEstado.ACTIVA == "activa"
    assert FuenteEstado.DESACTUALIZADA == "desactualizada"
    assert FuenteEstado.NO_DISPONIBLE == "no_disponible"

    # AlertaNivel
    assert AlertaNivel.ALTO == "alto"
    assert AlertaNivel.MEDIO == "medio"
    assert AlertaNivel.BAJO == "bajo"

    # AlertaTipo
    assert AlertaTipo.VARIACION_SIGNIFICATIVA == "variacion_significativa"
    assert AlertaTipo.CAMBIO_TENDENCIA == "cambio_tendencia"

    # IndicadorSlug esenciales
    assert IndicadorSlug.TASA_DESEMPLEO == "tasa_desempleo"
    assert IndicadorSlug.EMPLEO_TOTAL == "empleo_total"
    assert IndicadorSlug.INDICE_EMPLEABILIDAD == "indice_empleabilidad"

    # SectorEstrategico
    assert SectorEstrategico.TECNOLOGIA == "tecnologia"
    assert SectorEstrategico.SALUD == "salud"
    assert SectorEstrategico.ENERGIA == "energia"
    assert SectorEstrategico.TURISMO == "turismo"
    assert SectorEstrategico.ECONOMIA_CONOCIMIENTO == "economia-conocimiento"
