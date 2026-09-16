import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.paciente import PacienteModel
    from app.infrastructure.db.models.actividad import ActividadModel


class ProfesionalModel(Base):
    __tablename__ = "profesionales"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=True
    )

    # Relaciones
    pacientes: Mapped[List["PacienteModel"]] = relationship(
        "PacienteModel",
        back_populates="profesional",
        cascade="all, delete-orphan"
    )
    actividades: Mapped[List["ActividadModel"]] = relationship(
        "ActividadModel",
        back_populates="profesional",
        cascade="all, delete-orphan"
    )
