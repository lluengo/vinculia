from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.paciente import Paciente
from app.domain.ports.paciente_repository import PacienteRepositoryPort
from app.infrastructure.db.models.paciente import PacienteModel


class SqlPacienteRepository(PacienteRepositoryPort):
    """Implementación SQLAlchemy de PacienteRepositoryPort."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: PacienteModel) -> Paciente:
        return Paciente(
            id=model.id,
            profesional_id=model.profesional_id,
            apodo=model.apodo,
            edad=model.edad,
            creado_en=model.creado_en,
            eliminado_en=model.eliminado_en,
            ultima_sesion=model.ultima_sesion,
        )

    async def get_by_id(self, paciente_id: UUID) -> Optional[Paciente]:
        stmt = select(PacienteModel).where(PacienteModel.id == paciente_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_profesional(
        self, profesional_id: UUID, page: int = 1, size: int = 10, include_deleted: bool = False
    ) -> Tuple[List[Paciente], int]:
        filters = [PacienteModel.profesional_id == profesional_id]
        if not include_deleted:
            filters.append(PacienteModel.eliminado_en.is_(None))

        # Total count
        count_stmt = select(func.count(PacienteModel.id)).where(*filters)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items paginados
        offset = (page - 1) * size
        stmt = (
            select(PacienteModel)
            .where(*filters)
            .order_by(PacienteModel.creado_en.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def create(self, paciente: Paciente) -> Paciente:
        model = PacienteModel(
            id=paciente.id or None,
            profesional_id=paciente.profesional_id,
            apodo=paciente.apodo,
            edad=paciente.edad,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, paciente: Paciente) -> Paciente:
        stmt = select(PacienteModel).where(PacienteModel.id == paciente.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Paciente con ID {paciente.id} no encontrado")

        model.apodo = paciente.apodo
        model.edad = paciente.edad
        if paciente.ultima_sesion:
            model.ultima_sesion = paciente.ultima_sesion
        if paciente.eliminado_en:
            model.eliminado_en = paciente.eliminado_en

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, paciente_id: UUID) -> bool:
        stmt = select(PacienteModel).where(PacienteModel.id == paciente_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.eliminado_en = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.flush()
        return True
