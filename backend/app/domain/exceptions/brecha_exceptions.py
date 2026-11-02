"""Excepciones de dominio para el calculo de brechas de habilidades."""

from app.domain.exceptions.base import DomainException


class OcupacionNoEncontradaError(DomainException):
    """Se lanza cuando no existen datos para la ocupacion solicitada."""

    def __init__(self, ocupacion: str):
        self.ocupacion = ocupacion
        super().__init__(
            f"No se encontraron datos de brecha para la ocupacion: '{ocupacion}'"
        )
