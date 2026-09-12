import uuid
from datetime import datetime
from typing import List, Optional, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.profesional import ProfesionalModel
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
    tipo_plantilla: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    configuracion: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
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
    sesiones_juego: Mapped[List["SesionJuegoModel"]] = relationship(
        "SesionJuegoModel",
        back_populates="actividad",
        cascade="all, delete-orphan"
    )
