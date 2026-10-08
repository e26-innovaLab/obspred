"""Excepciones de dominio para el cálculo y consulta del Índice de Empleabilidad."""

from app.domain.exceptions.base import DomainException


class InvalidOccupationException(DomainException):
    """Excepción lanzada cuando la ocupación suministrada no cumple con el formato."""

    def __init__(
        self,
        message: str = "El identificador o nombre de ocupación no es válido.",
    ) -> None:
        """Inicializa la excepción con un mensaje explicativo.

        Args:
            message: Mensaje descriptivo de la regla infringida.
        """
        super().__init__(message)


class InsufficientDataException(DomainException):
    """Excepción cuando no existen datos suficientes para computar el índice."""

    def __init__(
        self,
        message: str = (
            "Datos insuficientes para computar el índice de empleabilidad."
        ),
    ) -> None:
        """Inicializa la excepción con un mensaje explicativo.

        Args:
            message: Mensaje descriptivo de la falta de datos.
        """
        super().__init__(message)
