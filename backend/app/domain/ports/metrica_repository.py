from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime
from app.application.dtos.metrica import (
    PacienteResumenMetricasDTO,
    EvolucionItemDTO,
    RendimientoActividadDTO,
    GlobalResumenDTO,
    RankingPacienteItemDTO,
)


class MetricaRepositoryPort(ABC):
    """Puerto para acceso a datos y agregaciones de métricas y evaluación."""

    @abstractmethod
    async def get_resumen_paciente(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> Optional[PacienteResumenMetricasDTO]:
        """Obtiene el resumen consolidado de métricas para un paciente dado."""
        pass

    @abstractmethod
    async def get_evolucion_paciente(
        self,
        profesional_id: UUID,
        paciente_id: UUID,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        agrupacion: str = "dia",
    ) -> List[EvolucionItemDTO]:
        """Obtiene la serie temporal de evolución agrupada por día o semana."""
        pass

    @abstractmethod
    async def get_rendimiento_por_actividad(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> List[RendimientoActividadDTO]:
        """Obtiene el rendimiento del paciente agrupado por actividad."""
        pass

    @abstractmethod
    async def get_sesiones_export(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Devuelve el apodo del paciente y la lista de registros planos para exportación a CSV."""
        pass

    @abstractmethod
    async def get_resumen_global(
        self, profesional_id: UUID
    ) -> GlobalResumenDTO:
        """Obtiene el resumen global de pacientes y actividades para el profesional."""
        pass

    @abstractmethod
    async def get_ranking_pacientes(
        self, profesional_id: UUID, orden: str = "progreso"
    ) -> List[RankingPacienteItemDTO]:
        """Obtiene la lista de pacientes clasificados por progreso o por actividad."""
        pass
