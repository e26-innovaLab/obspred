"""Esquemas Pydantic para los endpoints del módulo de Ingesta."""

from typing import Optional

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
    content_type: Optional[str] = Field(
        default=None,
        description="Tipo MIME del archivo informado por el cliente",
        examples=["text/csv"],
    )


FileUploadResponseSchema = ApiResponse[FileUploadData]
