from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class Paciente:
    apodo: str
    profesional_id: Optional[UUID] = None
    edad: Optional[int] = None
    id: Optional[UUID] = None
    creado_en: Optional[datetime] = None
    eliminado_en: Optional[datetime] = None
    ultima_sesion: Optional[datetime] = None
