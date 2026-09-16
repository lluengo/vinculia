from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class Profesional:
    email: str
    password_hash: str
    id: Optional[UUID] = None
    creado_en: Optional[datetime] = None
