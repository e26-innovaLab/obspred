from enum import Enum
from typing import List,Optional
from pydantic import BaseModel, ConfigDict, Field

class TipoDatoBrecha(str,Enum):
    OBSERVADO= "observado"
    CALCULADO="calculado"
    ESTIMADO="estimado"

class TipoHabilidad(str, Enum):
    TECNICA="tecnica"
    BLANDA="blanda"
class NivelBrecha(str,Enum):
    BAJA="baja"
    MEDIA="media"
    ALTA="alta"
    CRITICA="critica"

class MetadatosFuente(BaseModel):
    """Trazabilidad exigida por el brief y el equipo de Data."""
    model_config = ConfigDict(frozen=True)
    fuente: str = Field(..., description="Organismo o taxonomía de origen", examples=["SENCE SABE / ESCO"])
    fecha_actualizacion: str = Field(..., description="Fecha de corte del dato", examples=["2026-09-30"])
    metodologia: Optional[str] = Field(
            None,
            description="Aclaración metodológica o taxonomía de referencia",
            examples=["Taxonomía de referencia ESCO con demanda observada en avisos SABE."]
        )


class HabilidadBrechaItem(BaseModel):
    """Representa una barra del gráfico Demanda vs Oferta formativa."""
    model_config= ConfigDict(frozen=True)

    nombre: str= Field(..., description="Nombre de la habilidad", examples=["Trabajo en equipo remoto"])
    demanda: float= Field(...,description="", examples=[92.0])
    oferta: float = Field(...,description="", examples=[28.0])
    brecha: float = Field(...,description="", examples=[64.0])
    es_emergente: bool = Field(False,description="Indica si destaca en la lista de habilidades emergentes")

class BrechasResponse(BaseModel):
    """Contrato de respuesta para la pantalla de Brechas de habilidades."""
    model_config= ConfigDict(frozen=True)

    pais: str = Field(...,description="Código de país consultado (ARG, URY, CHL)", examples=["ARG"])
    sector: Optional[str] = Field(None, description="Sector económico", examples=["Tecnologias"])
    ocupacion: str = Field(...,description="Ocupacion analizada", examples=["desarrollador_software"])
    habilidades: List[HabilidadBrechaItem]= Field(..., description="Listado de habilidades para el gráfico comparativo")
    metadatos:MetadatosFuente