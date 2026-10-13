from enum import Enum

class FuenteEstado(str, Enum):
    """Enum que representa los posibles estados de una fuente de datos."""
    
    ACTIVA = "activa"
    DESACTUALIZADA = "desactualizada"
    NO_DISPONIBLE = "no_disponible"