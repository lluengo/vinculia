from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort
from app.infrastructure.db.models.profesional import ProfesionalModel


class SqlProfesionalRepository(ProfesionalRepositoryPort):
    """Implementación de repositorio SQL usando SQLAlchemy asíncrono."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ProfesionalModel) -> Profesional:
        return Profesional(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            creado_en=model.creado_en,
        )

    async def get_by_id(self, profesional_id: UUID) -> Optional[Profesional]:
        stmt = select(ProfesionalModel).where(ProfesionalModel.id == profesional_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[Profesional]:
        stmt = select(ProfesionalModel).where(ProfesionalModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, profesional: Profesional) -> Profesional:
        model = ProfesionalModel(
            id=profesional.id,
            email=profesional.email.lower().strip(),
            password_hash=profesional.password_hash,
            creado_en=profesional.creado_en,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, profesional: Profesional) -> Profesional:
        stmt = select(ProfesionalModel).where(ProfesionalModel.id == profesional.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Profesional con ID {profesional.id} no encontrado para actualizar.")
        
        model.email = profesional.email.lower().strip()
        model.password_hash = profesional.password_hash
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)
