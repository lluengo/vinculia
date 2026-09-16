import uuid
from datetime import datetime
from typing import List, Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.profesional import ProfesionalModel
    from app.infrastructure.db.models.paciente import PacienteModel
    from app.infrastructure.db.models.sesion_juego import SesionJuegoModel


class ActividadModel(Base):
    __tablename__ = "actividades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    profesional_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profesionales.id", ondelete="CASCADE"),
        nullable=True
    )
    paciente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id", ondelete="SET NULL"),
        nullable=True
    )
    tipo_plantilla: Mapped[str] = mapped_column(
        String(50),
        default="asociacion",
        nullable=False
    )
    titulo: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    descripcion: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    modo: Mapped[str] = mapped_column(
        String(50),
        default="imagen-imagen",
        nullable=False
    )
    pares: Mapped[list[Any]] = mapped_column(
        JSONB,
        default=list,
        nullable=False
    )
    configuracion: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    token_acceso: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True
    )
    expira_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    activa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    eliminado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=True
    )

    # Relaciones
    profesional: Mapped[Optional["ProfesionalModel"]] = relationship(
        "ProfesionalModel",
        back_populates="actividades"
    )
    paciente: Mapped[Optional["PacienteModel"]] = relationship(
        "PacienteModel",
        back_populates="actividades"
    )
    sesiones_juego: Mapped[List["SesionJuegoModel"]] = relationship(
        "SesionJuegoModel",
        back_populates="actividad",
        cascade="all, delete-orphan"
    )
