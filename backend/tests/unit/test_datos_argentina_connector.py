"""Pruebas unitarias para el conector de Datos Argentina."""

from app.infrastructure.connectors.datos_argentina_connector import (
    DatosArgentinaConnector,
)


def test_parse_period_and_quarter_trimestral() -> None:
    """Verifica que fechas ISO trimestrales se desagreguen en año y trimestre."""
    connector = DatosArgentinaConnector()

    y1, q1 = connector._parse_period_and_quarter("2023-01-01", "trimestral")
    assert y1 == "2023"
    assert q1 == "Q1"

    y2, q2 = connector._parse_period_and_quarter("2023-04-01", "trimestral")
    assert y2 == "2023"
    assert q2 == "Q2"

    y3, q3 = connector._parse_period_and_quarter("2023-07-01", "trimestral")
    assert y3 == "2023"
    assert q3 == "Q3"

    y4, q4 = connector._parse_period_and_quarter("2023-10-01", "trimestral")
    assert y4 == "2023"
    assert q4 == "Q4"


def test_parse_period_and_quarter_anual() -> None:
    """Verifica que fechas anuales retornen el año y trimestre en None."""
    connector = DatosArgentinaConnector()

    year, quarter = connector._parse_period_and_quarter("2024-01-01", "anual")
    assert year == "2024"
    assert quarter is None


def test_parse_series_payload_trimestral() -> None:
    """Verifica la normalización completa de un payload trimestral."""
    connector = DatosArgentinaConnector()
    metadata = {
        "id": "155.1_TLTAL_C_0_0_5",
        "nombre": "Total empleo registrado",
        "sector": None,
        "ocupacion": None,
        "unidad": "puestos de trabajo",
        "frecuencia": "trimestral",
        "dimension_geografica": "nacional",
    }
    payload = {
        "data": [
            ["2023-07-01", 6815041.0],
            ["2023-10-01", 6808249.0],
        ]
    }

    records = connector._parse_series_payload(
        payload=payload,
        slug="empleo_registrado_total",
        metadata=metadata,
    )

    assert len(records) == 2

    assert records[0].pais == "ARG"
    assert records[0].indicador == "empleo_registrado_total"
    assert records[0].periodo == "2023"
    assert records[0].trimestre == "Q3"
    assert records[0].valor == 6815041.0
    assert records[0].metadatos["fecha_referencia"] == "2023-07-01"

    assert records[1].periodo == "2023"
    assert records[1].trimestre == "Q4"
    assert records[1].valor == 6808249.0
    assert records[1].metadatos["fecha_referencia"] == "2023-10-01"
