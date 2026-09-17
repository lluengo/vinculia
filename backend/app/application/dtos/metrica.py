from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PacienteInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    apodo: str
    edad: Optional[int] = None


class UltimaSesionDTO(BaseModel):
    fecha: Optional[datetime] = None
    tiempo: int = 0
    aciertos: int = 0
    errores: int = 0


class PacienteResumenMetricasDTO(BaseModel):
    paciente: PacienteInfoDTO
    total_sesiones: int
    tiempo_promedio_seg: float
    tasa_acierto_promedio: float
    ultima_sesion: Optional[UltimaSesionDTO] = None
    tendencia: str = Field(
        ...,
        description="'mejora' | 'estable' | 'retroceso' | 'sin_datos'"
    )


class EvolucionItemDTO(BaseModel):
    fecha: str
    sesiones: int
    tiempo_promedio: float
    tasa_acierto: float


class RendimientoActividadDTO(BaseModel):
    actividad_id: Optional[UUID] = None
    titulo: str
    sesiones: int
    tiempo_promedio: float
    tasa_acierto: float


class GlobalResumenDTO(BaseModel):
    total_pacientes: int
    total_sesiones: int
    total_actividades: int
    tasa_acierto_promedio: float
    pacientes_activos_ultimos_7_dias: int


class RankingPacienteItemDTO(BaseModel):
    paciente_id: UUID
    apodo: str
    edad: Optional[int] = None
    total_sesiones: int
    tasa_acierto_promedio: float
    tendencia: str
    ultima_sesion: Optional[datetime] = None
