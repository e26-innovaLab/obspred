from enum import StrEnum

from pydantic import BaseModel


class TipoDato(StrEnum):
    HISTORICO = "historico"
    PROYECCION = "proyeccion"



class PuntoSerie(BaseModel):
    periodo: str  # "T1 2025"
    valor: float
    es_destacado: bool = False  # Para pintar el circulo amarillo en la UI


class PuntoProyeccion(BaseModel):
    periodo: str
    valor_estimado: float
    valor_inferior: float | None = None
    valor_superior: float | None = None


class CambioSignificativo(BaseModel):
    periodo: str
    titulo: str
    descripcion: str
    tipo_alerta: str | None = "info"


class MetadatosFuente(BaseModel):
    fuente: str
    fecha: str
    metodologia: str | None = None


class TendenciasResponse(BaseModel):
    pais: str
    sector: str
    ocupacion: str
    indicador: str
    serie_historica: list[PuntoSerie]
    cambios_significativos: list[CambioSignificativo]
    proyeccion: list[PuntoProyeccion]
    metadatos_historico: MetadatosFuente
    metadatos_proyeccion: MetadatosFuente
