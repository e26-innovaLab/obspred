"""Contrato de interfaz (puerto) para validadores de archivos."""

from abc import ABC, abstractmethod


class IFileValidator(ABC):
    """Interfaz abstracta para validación de archivos de entrada (SRP y OCP)."""

    @abstractmethod
    def validate(self, filename: str, content: bytes) -> None:
        """Aplica las reglas de negocio sobre el archivo antes de su persistencia.

        Args:
            filename: Nombre provisto del archivo.
            content: Contenido binario del archivo.

        Raises:
            DomainException: Si alguna regla de validación de negocio se incumple.
        """
        pass
