"""Excepciones de dominio para el módulo de indicadores y series temporales."""


class IndicadorError(Exception):
    """Excepción base para errores de negocio en indicadores."""

    pass


class SerieNoEncontradaError(IndicadorError):
    """Se lanza cuando no existen registros para el país e indicador solicitados."""

    def __init__(self, pais: str, indicador: str, detalle: str = "") -> None:
        self.pais = pais
        self.indicador = indicador
        msg = f"No se encontró serie histórica para el país '{pais}' y el indicador '{indicador}'."
        if detalle:
            msg = f"{msg} {detalle}"
        super().__init__(msg)


class ParametrosRangoInvalidosError(IndicadorError):
    """Se lanza cuando los filtros de fecha o período temporal son inconsistentes."""

    pass