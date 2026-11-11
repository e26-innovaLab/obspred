from collections import defaultdict

from app.api.v1.schemas.alertas_schema import AlertaItemDto
from app.core.constants import UMBRAL_ALERTA_ALTO, UMBRAL_ALERTA_MEDIO
from app.domain.interfaces.indicador_repository import IIndicadorRepository


class AlertaService:
    def __init__(self, indicador_repository: IIndicadorRepository) -> None:
        self._indicador_repository = indicador_repository


    async def get_alertas (
            self,
            pais: str | None = None,
            indicador: str | None = None,
            sector: str | None = None,
            tipo: str | None = None
    )-> list[AlertaItemDto]:
        """Procesa la consulta de alertas estadísticas.

        Args:
            tipo: Clasificación de la alerta solicitada.
            indicador: Filtro opcional por slug de indicador.
            pais: Filtro opcional por código ISO 3166-1 alpha-3.
            sector: Filtro opcional por sector estratégico.

        Returns:
            list[AlertaItemDto]: Lista de eventos de alerta detectados.
        """

        #1. Obtener los indicadores según los filtros proporcionados
        indicadores = await self._indicador_repository.get_by_filters(
           pais=pais,
           sector=sector,
           indicador=indicador
        )

        #2. Agrupar registros a la misma serie
        series_dict = defaultdict(list)

        for registro in indicadores:
            clave_serie = (
                registro.pais,
                registro.sector,
                registro.ocupacion,
                registro.indicador,
                registro.fuente
            )
            series_dict[clave_serie].append(registro)

        alertas: list[AlertaItemDto] = []

        #3. Calcular variaciones interperíodo y generar alertas
        for registros in series_dict.values():
            registros.sort(key=lambda x: x.periodo)

            if len(registros) < 2:
                continue

            anterior = registros[-2]
            actual = registros[-1]

            #Evitar divisiones por cero
            if anterior.valor == 0:
                continue

            #calcular variaciones

            variacion_pct = (
                (actual.valor - anterior.valor) /  abs (anterior.valor)
            ) * 100

            mangnitud = abs(variacion_pct)

            #Determinar el nivel de alerta según los umbrales definidos
            if mangnitud >= UMBRAL_ALERTA_ALTO:
                nivel = "alto"
            elif mangnitud >= UMBRAL_ALERTA_MEDIO:
                nivel = "medio"
            else:
                continue


            #Determinar el tipo de alerta según la variación
            tipo_generado = self._clasificar_tipo (actual.indicador)

            if tipo and tipo != tipo_generado:
                continue


            #Generar titulo y descripcion
            titulo,descripcion = self._generar_titulo_descripcion(
                indicador=actual.indicador,
                variacion_pct=variacion_pct,
                periodo=actual.periodo,
            )

            #Crear objeto de alerta
            alertas.append(
                AlertaItemDto(
                    id = (
                        f"{actual.indicador}-{actual.pais}-{actual.periodo}")
                    ),
                    pais = actual.pais,
                    indicador = actual.indicador,
                    periodo = str (actual.periodo),
                    variacion_pct = round(variacion_pct,2),
                    nivel = nivel,
                    titulo = titulo,
                    descripcion = descripcion
                )
        return alertas

    @staticmethod
    def _clasificar_tipo(indicador: str) -> str:
        """Clasifica el tipo de alerta según el indicador."""
        nombre = indicador.lower()

        indicadores_empleo = (
            "empleo",
            "desempleo",
            "desocupacion",
            "desocupación",
            "subocupacion",
            "subocupación",
            "actividad",

        )
        if any(palabras in nombre for palabras in indicadores_empleo):
            return "variacion_significativa"

        return "Variacion_significativa"

    @staticmethod
    def _generar_titulo_descripcion(
        indicador: str,
        variacion_pct: float,
        periodo: str
    ) -> tuple[str, str]:
        """Genera el título y la descripción de la alerta según el indicador y la variación."""
        nombres = {
             "tasa_desempleo": "Desempleo",
            "tasa_desocupacion_total": "Desempleo",
            "tasa_empleo_total": "Empleo",
            "tasa_actividad_total": "Actividad",
            "tasa_subocupacion_total": "Subocupación"
        }

        nombre = nombres.get(
            indicador,
            indicador.replace("_", " ").capitalize()
        )

        porcentaje = f"{abs(variacion_pct):.1f}".replace(".", ",")

        if variacion_pct < 0:
            titulo = f"{nombre}: reducción del {porcentaje} %"
            descripcion = (
                f"Mejora en el indicador {nombre} en el período {periodo}."
            )
        else:
            titulo = f"{nombre}: suba de {porcentaje} %"
            descripcion = (
                f"Incremento en el indicador {nombre} en el período {periodo}."
            )
        return titulo, descripcion



