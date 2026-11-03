"""Excepciones de dominio para el conector y procesamiento de SIMEL Chile."""

from app.domain.exceptions.base import DomainException


class SimelWafBlockedException(DomainException):
    """Excepción lanzada cuando el acceso a SIMEL es bloqueado por WAF."""

    def __init__(
        self,
        message: str = (
            "La plataforma oficial de SIMEL Chile (www.simel.gob.cl) se encuentra "
            "protegida por el WAF de Huawei Cloud (HTTP 418 / desafío anti-bot), "
            "lo que restringe consultas REST automatizadas desatendidas. "
            "Para incorporar información de SIMEL, descargue el reporte oficial "
            "y cárguelo a través del endpoint POST /api/v1/ingesta/upload/simel."
        ),
    ) -> None:
        """Inicializa la excepción con el diagnóstico y la alternativa operativa.

        Args:
            message: Descripción detallada del bloqueo y flujo de resolución.
        """
        super().__init__(message)


class InvalidSimelCsvException(DomainException):
    """Excepción lanzada cuando un archivo CSV de SIMEL no es válido."""

    def __init__(self, filename: str, reason: str) -> None:
        """Inicializa la excepción con el archivo y la causa del fallo.

        Args:
            filename: Nombre del archivo CSV procesado.
            reason: Motivo técnico de la invalidez sintáctica o estructural.
        """
        message = f"El archivo exportado de SIMEL '{filename}' no es válido: {reason}"
        super().__init__(message)
        self.filename = filename
        self.reason = reason
