"""Configuración de registro estructurado (logging) de la aplicación."""

import logging
import sys
from typing import Optional

from app.core.constants import PROJECT_IDENTIFIER


def get_logger(
    name: Optional[str] = None, log_level: Optional[str] = None
) -> logging.Logger:
    """Obtiene o inicializa una instancia de logger configurada.

    Args:
        name: Subnombre opcional del logger. Si se omite, se usa el identificador base.
        log_level: Nivel de registro (DEBUG, INFO, WARNING, ERROR). Por defecto INFO.

    Returns:
        logging.Logger: Instancia del logger lista para emitir eventos formateados.
    """
    logger_name = f"{PROJECT_IDENTIFIER}.{name}" if name else PROJECT_IDENTIFIER
    logger = logging.getLogger(logger_name)

    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = get_logger()
