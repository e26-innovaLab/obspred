"""Entidades y objetos de valor del dominio para el Índice de Empleabilidad."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class DimensionIndice:
    """Dimensión individual ponderada que compone el Índice de Empleabilidad.

    Attributes:
        nombre: Denominación de la dimensión analítica.
        valor: Puntuación normalizada de la dimensión (0.0 a 100.0).
        peso: Ponderación o coeficiente relativo en el índice global (0.0 a 1.0).
        descripcion: Resumen explicativo o metodológico de la dimensión.
    """

    nombre: str
    valor: float
    peso: float
    descripcion: Optional[str] = None

    def __post_init__(self) -> None:
        """Valida invariantes de la dimensión tras inicializarse.

        Raises:
            ValueError: Si algún valor no cumple las restricciones numéricas.
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la dimensión no puede estar vacío.")
        if not (0.0 <= self.valor <= 100.0):
            raise ValueError(
                f"El valor de dimensión '{self.nombre}' debe situarse entre 0 y 100."
            )
        if not (0.0 <= self.peso <= 1.0):
            raise ValueError(
                f"El peso de la dimensión '{self.nombre}' debe estar entre 0.0 y 1.0."
            )


@dataclass(frozen=True)
class EvolucionIndicePunto:
    """Punto temporal en la serie histórica del Índice de Empleabilidad.

    Attributes:
        periodo: Etiqueta del período temporal analizado (ej. '2025-Q3').
        valor: Puntuación calculada del índice en el período (0.0 a 100.0).
    """

    periodo: str
    valor: float

    def __post_init__(self) -> None:
        """Valida invariantes del punto histórico.

        Raises:
            ValueError: Si el período o valor son inválidos.
        """
        if not self.periodo or not self.periodo.strip():
            raise ValueError("El período no puede estar vacío.")
        if not (0.0 <= self.valor <= 100.0):
            raise ValueError("El valor de evolución debe situarse entre 0.0 y 100.0.")


@dataclass(frozen=True)
class IndiceEmpleabilidad:
    """Entidad principal del Índice de Empleabilidad para una ocupación.

    Attributes:
        ocupacion_id: Identificador normalizado de la ocupación (ej. 'dev-software').
        ocupacion_nombre: Nombre legible y representativo de la ocupación.
        score: Score general agregado del índice en escala de 0.0 a 100.0.
        nivel: Clasificación cualitativa ('Muy Alto', 'Alto', 'Medio', 'Bajo').
        dimensiones: Desglose de las dimensiones metodológicas ponderadas.
        tipo: Tipo metodológico del indicador (por defecto 'calculado').
        fuente: Organismos o fuentes oficiales armonizadas de procedencia.
        fecha_actualizacion: Fecha de corte o actualización metodológica.
        metodologia: Descripción explicativa del algoritmo y coeficientes.
        pais: País de referencia si fue provisto en los filtros de consulta.
        sector: Sector estratégico asociado.
        periodo: Período de referencia temporal analizado.
        evolucion: Serie temporal histórica de puntos del índice.
    """

    ocupacion_id: str
    ocupacion_nombre: str
    score: float
    nivel: str
    dimensiones: List[DimensionIndice]
    tipo: str = "calculado"
    fuente: str = "Observatorio Predictivo / Fuentes Oficiales Armonizadas"
    fecha_actualizacion: date = field(default_factory=date.today)
    metodologia: str = (
        "Índice de Empleabilidad — Metodología v1 (ponderación multidimensional: "
        "Demanda 35%, Estabilidad salarial 25%, Cobertura formativa 20%, "
        "Crecimiento reciente 20%)"
    )
    pais: Optional[str] = None
    sector: Optional[str] = None
    periodo: Optional[str] = None
    evolucion: List[EvolucionIndicePunto] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Valida invariantes de la entidad tras su inicialización.

        Raises:
            ValueError: Si el identificador o score son inválidos.
        """
        if not self.ocupacion_id or not self.ocupacion_id.strip():
            raise ValueError("El ID de la ocupación no puede estar vacío.")
        if not (0.0 <= self.score <= 100.0):
            raise ValueError(
                "El score global debe situarse en el intervalo [0.0, 100.0]."
            )

    @classmethod
    def determinar_nivel(cls, score: float) -> str:
        """Determina la clasificación cualitativa según la escala definida.

        Args:
            score: Valor numérico entre 0.0 y 100.0.

        Returns:
            str: 'Muy Alto', 'Alto', 'Medio' o 'Bajo'.
        """
        if score >= 80.0:
            return "Muy Alto"
        if score >= 65.0:
            return "Alto"
        if score >= 50.0:
            return "Medio"
        return "Bajo"

    @classmethod
    def calcular_score_ponderado(cls, dimensiones: List[DimensionIndice]) -> float:
        """Calcula el score global ponderado a partir de sus dimensiones.

        Args:
            dimensiones: Lista de dimensiones con valores y pesos.

        Returns:
            float: Score ponderado redondeado a dos decimales.
        """
        if not dimensiones:
            return 0.0
        peso_acumulado = sum(d.peso for d in dimensiones)
        if peso_acumulado == 0:
            return 0.0
        score = sum(d.valor * d.peso for d in dimensiones) / peso_acumulado
        return round(score, 2)
