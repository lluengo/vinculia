import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.paciente import PacienteModel
    from app.infrastructure.db.models.actividad import ActividadModel


class SesionJuegoModel(Base):
    __tablename__ = "sesiones_juego"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    paciente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=True
    )
    actividad_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("actividades.id", ondelete="CASCADE"),
        nullable=True
    )
    tiempo_segundos: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    aciertos: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    errores: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    completado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=True
    )

    # Relaciones
    paciente: Mapped[Optional["PacienteModel"]] = relationship(
        "PacienteModel",
        back_populates="sesiones_juego"
    )
    actividad: Mapped[Optional["ActividadModel"]] = relationship(
        "ActividadModel",
        back_populates="sesiones_juego"
    )
