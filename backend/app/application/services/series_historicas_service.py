"""Servicio de aplicación para la consulta y orquestación de Series Históricas."""

from app.application.dtos.series_historicas_dto import (
    ConsultaSerieHistoricaDTO,
    PuntoSerieDTO,
    SerieHistoricaResultadoDTO,
)
from app.domain.entities.serie_historica import SerieHistorica
from app.domain.exceptions.indicador_exceptions import SerieNoEncontradaError
from app.domain.interfaces.serie_historica_repository import (
    ISerieHistoricaRepository,
)


class SeriesHistoricasService:
    """Caso de uso para la obtención y armado de series temporales de indicadores."""

    def __init__(self, repository: ISerieHistoricaRepository) -> None:
        self._repository = repository

    async def ejecutar(
        self, consulta: ConsultaSerieHistoricaDTO
    ) -> SerieHistoricaResultadoDTO:
        """Ejecuta el caso de uso y retorna el DTO de resultado."""
        pais_norm = consulta.pais.strip().upper()
        indicador_norm = consulta.indicador.strip().lower()

        puntos_dominio = await self._repository.get_serie_temporal(
            pais=pais_norm,
            indicador=indicador_norm,
            sector=consulta.sector,
            periodo_desde=consulta.periodo_desde,
            periodo_hasta=consulta.periodo_hasta,
        )

        if not puntos_dominio:
            raise SerieNoEncontradaError(
                pais=pais_norm,
                indicador=indicador_norm,
                detalle="No se registraron observaciones para el filtro indicado.",
            )

        # Construcción de la entidad para validar invariantes de dominio
        serie = SerieHistorica(
            pais=pais_norm,
            indicador=indicador_norm,
            observaciones=puntos_dominio,
            sector=consulta.sector,
            periodo_desde=consulta.periodo_desde,
            periodo_hasta=consulta.periodo_hasta,
        )

        # Mapeo de salida a DTO
        return SerieHistoricaResultadoDTO(
            pais=serie.pais,
            indicador=serie.indicador,
            sector=serie.sector,
            total_observaciones=serie.total_observaciones,
            observaciones=[
                PuntoSerieDTO(
                    periodo=p.periodo,
                    valor=p.valor,
                    tipo=p.tipo,
                    fuente=p.fuente,
                )
                for p in serie.observaciones
            ],
        )
