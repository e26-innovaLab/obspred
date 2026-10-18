"""Esquemas Pydantic para los endpoints del módulo de Ingesta."""

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse


class FileUploadData(BaseModel):
    """Datos retornados tras la persistencia exitosa de un archivo.

    Attributes:
        filename: Nombre asignado al archivo almacenado en el sistema.
        original_filename: Nombre original provisto durante la carga.
        file_path: Ruta del archivo almacenado.
        size_bytes: Tamaño del archivo en bytes.
        content_type: Tipo de medio MIME del archivo.
    """

    model_config = ConfigDict(frozen=True)

    filename: str = Field(
        ...,
        description="Nombre único asignado al archivo en almacenamiento",
        examples=["1712490000_datos_empleo.csv"],
    )
    original_filename: str = Field(
        ...,
        description="Nombre original del archivo recibido",
        examples=["datos_empleo.csv"],
    )
    file_path: str = Field(
        ...,
        description="Ruta de persistencia física del archivo",
        examples=["data/uploads/1712490000_datos_empleo.csv"],
    )
    size_bytes: int = Field(
        ...,
        description="Tamaño total del archivo persistido en bytes",
        examples=[2048],
    )
    content_type: str | None = Field(
        default=None,
        description="Tipo MIME del archivo informado por el cliente",
        examples=["text/csv"],
    )


FileUploadResponseSchema = ApiResponse[FileUploadData]


class SyncExternalDataRequestSchema(BaseModel):
    """Parámetros de solicitud para la sincronización de una fuente externa."""

    model_config = ConfigDict(extra="forbid")

    paises: list[str] | None = Field(
        default=None,
        description="Lista de códigos ISO de país (ej. ['ARG', 'URY', 'CHL'])",
        examples=[["ARG", "URY", "CHL"]],
    )
    indicadores: list[str] | None = Field(
        default=None,
        description="Lista de indicadores o códigos a sincronizar",
        examples=[["tasa_desempleo", "pib_per_capita"]],
    )
    periodo_desde: str | None = Field(
        default=None,
        description="Año o período inicial de extracción",
        examples=["2018"],
    )
    periodo_hasta: str | None = Field(
        default=None,
        description="Año o período final de extracción",
        examples=["2024"],
    )


class SyncExternalDataResponseData(BaseModel):
    """Resultado detallado de la sincronización externa ejecutada."""

    model_config = ConfigDict(frozen=True)

    source: str = Field(
        ...,
        description="Fuente externa procesada",
        examples=["World Bank"],
    )
    status: str = Field(
        ...,
        description="Estado del proceso ('success', 'failed')",
        examples=["success"],
    )
    total_fetched: int = Field(
        ...,
        description="Cantidad de registros obtenidos desde la API remota",
        examples=[18],
    )
    total_persisted: int = Field(
        ...,
        description="Cantidad de registros persistidos o actualizados",
        examples=[18],
    )
    execution_time_seconds: float = Field(
        ...,
        description="Tiempo de ejecución del proceso en segundos",
        examples=[1.42],
    )
    countries_synced: list[str] = Field(
        default_factory=list,
        description="Países efectivamente procesados",
        examples=[["ARG", "CHL", "URY"]],
    )
    indicators_synced: list[str] = Field(
        default_factory=list,
        description="Indicadores efectivamente procesados",
        examples=[["pib_per_capita", "tasa_desempleo"]],
    )
    error_message: str | None = Field(
        default=None,
        description="Mensaje de error en caso de fallo",
    )


SyncExternalDataResponseSchema = ApiResponse[SyncExternalDataResponseData]
