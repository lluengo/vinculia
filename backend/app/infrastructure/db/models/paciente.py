import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.profesional import ProfesionalModel
    from app.infrastructure.db.models.sesion_juego import SesionJuegoModel


class PacienteModel(Base):
    __tablename__ = "pacientes"
    __table_args__ = (
        CheckConstraint("edad > 0", name="pacientes_edad_check"),
    )

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
    apodo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    edad: Mapped[Optional[int]] = mapped_column(
        Integer,
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
        back_populates="pacientes"
    )
    sesiones_juego: Mapped[List["SesionJuegoModel"]] = relationship(
        "SesionJuegoModel",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
