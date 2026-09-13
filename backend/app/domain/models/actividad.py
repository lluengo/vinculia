from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


@dataclass
class Actividad:
    titulo: str
    profesional_id: Optional[UUID] = None
    paciente_id: Optional[UUID] = None
    tipo_plantilla: str = "asociacion"
    descripcion: Optional[str] = None
    modo: str = "imagen-imagen"
    pares: List[Dict[str, Any]] = field(default_factory=list)
    configuracion: Dict[str, Any] = field(default_factory=dict)
    token_acceso: Optional[str] = None
    expira_en: Optional[datetime] = None
    activa: bool = True
    eliminado_en: Optional[datetime] = None
    id: Optional[UUID] = None
    creado_en: Optional[datetime] = None
