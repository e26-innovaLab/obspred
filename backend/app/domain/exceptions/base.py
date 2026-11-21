"""Excepciones base del dominio de la aplicación."""


class DomainException(Exception):
    """Excepción raíz para todas las violaciones de invariantes o reglas del negocio."""

    def __init__(self, message: str) -> None:
        """Inicializa la excepción con un mensaje explicativo.

        Args:
            message: Descripción comprensible del error ocurrido.
        """
        super().__init__(message)
        self.message = message


class EntityNotFoundException(DomainException):
    """Excepción lanzada cuando una entidad requerida no existe en el sistema."""

    def __init__(self, entity_name: str, entity_id: str) -> None:
        """Inicializa la excepción indicando la entidad y el identificador faltante.

        Args:
            entity_name: Nombre o tipo de la entidad no localizada.
            entity_id: Clave primaria o identificador buscado.
        """
        message = f"La entidad '{entity_name}' con ID '{entity_id}' no fue encontrada."
        super().__init__(message)
        self.entity_name = entity_name
        self.entity_id = entity_id


class DatabaseConnectionException(DomainException):
    """Excepción lanzada cuando falla la conexión con el motor de base de datos."""

    def __init__(
        self,
        message: str = (
            "No se pudo establecer conexión con el servicio de base de datos."
        ),
        detail: str | None = None,
    ) -> None:
        """Inicializa la excepción indicando la indisponibilidad de la base de datos.

        Args:
            message: Mensaje general del error.
            detail: Detalle específico de diagnóstico para el cliente.
        """
        super().__init__(message)
        self.detail = detail or (
            "El servicio de base de datos se encuentra fuera de línea o inaccesible. "
            "Verifique que el servidor de base de datos esté activo y accesible."
        )
