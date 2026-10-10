from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class TipoDato(str,Enum):
    HISTORICO = "historico"
    PROYECCION = "proyeccion"

class PuntoSerie(BaseModel):
    periodo: str # "T1 2025"
    valor: float
    es_destacado: bool = False # Para pintar el circulo amarillo en la UI

class PuntoProyeccion(BaseModel):
    periodo:str
    valor_estimado:float
    valor_inferior: Optional[float] = None
    valor_superior: Optional[float] = None

class CambioSignificativo(BaseModel):
    periodo: str
    titulo: str
    descripcion:str
    tipo_alerta: Optional[str] = "info"


class MetadatosFuente(BaseModel):
      fuente: str
      fecha: str
      metodologia: Optional[str]= None

class TendenciasResponse(BaseModel):
    pais: str
    sector: str
    ocupacion:str
    indicador: str
    serie_historica: List[PuntoSerie]
    cambios_significativos: List[CambioSignificativo]
    proyeccion: List[PuntoProyeccion]
    metadatos_historico: MetadatosFuente
    metadatos_proyeccion: MetadatosFuente


