from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class PacienteCreateDTO(BaseModel):
    apodo: str = Field(..., min_length=1, max_length=100, description="Seudónimo o nombre del paciente")
    edad: Optional[int] = Field(None, gt=0, lt=150, description="Edad en años")


class PacienteUpdateDTO(BaseModel):
    apodo: Optional[str] = Field(None, min_length=1, max_length=100)
    edad: Optional[int] = Field(None, gt=0, lt=150)


class PacienteResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profesional_id: Optional[UUID] = None
    apodo: str
    edad: Optional[int] = None
    creado_en: Optional[datetime] = None
    eliminado_en: Optional[datetime] = None
    ultima_sesion: Optional[datetime] = None


class PacienteListResponseDTO(BaseModel):
    items: List[PacienteResponseDTO]
    total: int
    page: int
    size: int
