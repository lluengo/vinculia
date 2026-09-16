from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


class ParDTO(BaseModel):
    origen_url: str = Field(..., description="Texto o URL del elemento origen")
    destino_url: str = Field(..., description="Texto o URL del elemento destino asociado")
    es_correcto: bool = Field(True, description="Indica si este par es una asociación correcta")


class ConfiguracionDTO(BaseModel):
    limite_tiempo_seg: int = Field(300, ge=10, le=3600, description="Tiempo límite en segundos")
    nivel_dificultad: int = Field(1, ge=1, le=5, description="Nivel de dificultad (1 a 5)")
    tamano_elementos: str = Field("mediano", description="pequeño, mediano, grande")
    tolerancia_errores: int = Field(3, ge=0, le=50, description="Cantidad máxima de errores permitidos")


class ActividadCreateDTO(BaseModel):
    paciente_id: Optional[UUID] = Field(None, description="ID del paciente al que se asigna")
    tipo_plantilla: str = Field("asociacion", description="Tipo de plantilla")
    titulo: str = Field(..., min_length=1, max_length=150, description="Título del ejercicio")
    descripcion: Optional[str] = Field(None, max_length=500, description="Instrucciones o descripción")
    modo: str = Field("imagen-imagen", description="imagen-imagen | imagen-sonido | texto-imagen")
    pares: List[ParDTO] = Field(default_factory=list, description="Lista de pares de asociación")
    configuracion: Optional[ConfiguracionDTO] = Field(default_factory=ConfiguracionDTO)


class ActividadUpdateDTO(BaseModel):
    paciente_id: Optional[UUID] = None
    tipo_plantilla: Optional[str] = None
    titulo: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    modo: Optional[str] = None
    pares: Optional[List[ParDTO]] = None
    configuracion: Optional[ConfiguracionDTO] = None
    activa: Optional[bool] = None


class ActividadResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profesional_id: Optional[UUID] = None
    paciente_id: Optional[UUID] = None
    tipo_plantilla: str
    titulo: str
    descripcion: Optional[str] = None
    modo: str
    pares: List[Dict[str, Any]]
    configuracion: Dict[str, Any]
    token_acceso: Optional[str] = None
    expira_en: Optional[datetime] = None
    activa: bool
    creado_en: Optional[datetime] = None


class ActividadListResponseDTO(BaseModel):
    items: List[ActividadResponseDTO]
    total: int
    page: int
    size: int


class EnlaceResponseDTO(BaseModel):
    token: str
    url_completa: str
    expira_en: datetime


class ActividadPublicaResponseDTO(BaseModel):
    id: UUID
    titulo: str
    descripcion: Optional[str] = None
    modo: str
    pares: List[Dict[str, Any]]
    configuracion: Dict[str, Any]
    apodo_paciente: Optional[str] = None


class SesionPublicaCreateDTO(BaseModel):
    actividad_id: Optional[UUID] = None
    token: Optional[str] = None
    tiempo_segundos: int = Field(..., ge=0)
    aciertos: int = Field(..., ge=0)
    errores: int = Field(..., ge=0)
