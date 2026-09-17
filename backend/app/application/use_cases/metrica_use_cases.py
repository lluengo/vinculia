import csv
import io
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date
from app.domain.ports.metrica_repository import MetricaRepositoryPort
from app.application.dtos.metrica import (
    PacienteResumenMetricasDTO,
    EvolucionItemDTO,
    RendimientoActividadDTO,
    GlobalResumenDTO,
    RankingPacienteItemDTO,
)


class GetPacienteResumenMetricasUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, paciente_id: UUID) -> PacienteResumenMetricasDTO:
        return await self.repo.get_resumen_paciente(profesional_id, paciente_id)


class GetPacienteEvolucionUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(
        self,
        profesional_id: UUID,
        paciente_id: UUID,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        agrupacion: str = "dia",
    ) -> List[EvolucionItemDTO]:
        if agrupacion not in ("dia", "semana"):
            agrupacion = "dia"
        return await self.repo.get_evolucion_paciente(
            profesional_id=profesional_id,
            paciente_id=paciente_id,
            desde=desde,
            hasta=hasta,
            agrupacion=agrupacion,
        )


class GetPacientePorActividadUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, paciente_id: UUID) -> List[RendimientoActividadDTO]:
        return await self.repo.get_rendimiento_por_actividad(profesional_id, paciente_id)


class ExportarSesionesPacienteUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, paciente_id: UUID) -> Tuple[str, str]:
        """
        Retorna (apodo, contenido_csv_string).
        """
        apodo, sesiones = await self.repo.get_sesiones_export(profesional_id, paciente_id)

        output = io.StringIO()
        fieldnames = [
            "sesion_id",
            "fecha",
            "actividad",
            "tiempo_segundos",
            "aciertos",
            "errores",
            "tasa_acierto",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for sesion in sesiones:
            writer.writerow(sesion)

        return apodo, output.getvalue()


class GetGlobalResumenUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID) -> GlobalResumenDTO:
        return await self.repo.get_resumen_global(profesional_id)


class GetRankingPacientesUseCase:
    def __init__(self, repo: MetricaRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, orden: str = "progreso") -> List[RankingPacienteItemDTO]:
        if orden not in ("progreso", "actividad"):
            orden = "progreso"
        return await self.repo.get_ranking_pacientes(profesional_id, orden=orden)
