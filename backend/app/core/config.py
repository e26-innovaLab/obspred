"""Configuración central de la aplicación basada en Pydantic Settings.

Permite cargar y validar variables de entorno desde archivos .env
o el entorno del sistema operativo sin acoplar cadenas fijas.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    API_V1_PREFIX,
    DEFAULT_MAX_UPLOAD_SIZE_BYTES,
    DEFAULT_UPLOAD_DIR,
    AppEnvironment,
)


class Settings(BaseSettings):
    """Clase principal de ajustes y parámetros del backend.

    Attributes:
        app_env: Entorno actual de ejecución tipado como AppEnvironment.
        app_name: Nombre público de la API.
        app_description: Resumen funcional del servicio.
        api_v1_prefix: Prefijo base para la ruta de endpoints versión 1.
        debug: Indicador de modo depuración.
        server_host: Dirección IP o interfaz de escucha del servidor.
        server_port: Puerto TCP asignado al servidor HTTP.
        cors_origins: Lista de orígenes autorizados para compartir recursos (CORS).
        database_url: Cadena de conexión URI a la base de datos relacional.
        database_echo: Habilita el registro de sentencias SQL generadas por el ORM.
        upload_dir: Ruta del directorio local para persistencia de archivos de ingesta.
        max_upload_size_bytes: Límite máximo en bytes para subida de archivos.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    app_name: str = "Observatorio Predictivo API"
    app_description: str = (
        "API backend de analítica socioeconómica, laboral y educativa "
        "para Argentina, Uruguay y Chile (innova.lab)."
    )
    api_v1_prefix: str = API_V1_PREFIX
    debug: bool = True

    server_host: str = "0.0.0.0"
    server_port: int = 8000

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    database_url: str = "sqlite+aiosqlite:///./obspred_dev.db"
    database_echo: bool = False

    upload_dir: str = DEFAULT_UPLOAD_DIR
    max_upload_size_bytes: int = DEFAULT_MAX_UPLOAD_SIZE_BYTES


# Instancia única reutilizable para inyección o importación directa
settings = Settings()
