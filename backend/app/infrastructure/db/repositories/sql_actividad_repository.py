from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.actividad import Actividad
from app.domain.ports.actividad_repository import ActividadRepositoryPort
from app.infrastructure.db.models.actividad import ActividadModel


class SqlActividadRepository(ActividadRepositoryPort):
    """Implementación SQLAlchemy de ActividadRepositoryPort."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ActividadModel) -> Actividad:
        return Actividad(
            id=model.id,
            profesional_id=model.profesional_id,
            paciente_id=model.paciente_id,
            tipo_plantilla=model.tipo_plantilla,
            titulo=model.titulo,
            descripcion=model.descripcion,
            modo=model.modo,
            pares=model.pares or [],
            configuracion=model.configuracion or {},
            token_acceso=model.token_acceso,
            expira_en=model.expira_en,
            activa=model.activa,
            eliminado_en=model.eliminado_en,
            creado_en=model.creado_en,
        )

    async def get_by_id(self, actividad_id: UUID) -> Optional[Actividad]:
        stmt = select(ActividadModel).where(ActividadModel.id == actividad_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_token(self, token: str) -> Optional[Actividad]:
        stmt = select(ActividadModel).where(
            ActividadModel.token_acceso == token,
            ActividadModel.eliminado_en.is_(None),
            ActividadModel.activa.is_(True),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_profesional(
        self,
        profesional_id: UUID,
        paciente_id: Optional[UUID] = None,
        tipo_plantilla: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        include_deleted: bool = False,
    ) -> Tuple[List[Actividad], int]:
        filters = [ActividadModel.profesional_id == profesional_id]
        if not include_deleted:
            filters.append(ActividadModel.eliminado_en.is_(None))
        if paciente_id:
            filters.append(ActividadModel.paciente_id == paciente_id)
        if tipo_plantilla:
            filters.append(ActividadModel.tipo_plantilla == tipo_plantilla)

        count_stmt = select(func.count(ActividadModel.id)).where(*filters)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        offset = (page - 1) * size
        stmt = (
            select(ActividadModel)
            .where(*filters)
            .order_by(ActividadModel.creado_en.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def create(self, actividad: Actividad) -> Actividad:
        model = ActividadModel(
            id=actividad.id or None,
            profesional_id=actividad.profesional_id,
            paciente_id=actividad.paciente_id,
            tipo_plantilla=actividad.tipo_plantilla,
            titulo=actividad.titulo,
            descripcion=actividad.descripcion,
            modo=actividad.modo,
            pares=actividad.pares,
            configuracion=actividad.configuracion,
            token_acceso=actividad.token_acceso,
            expira_en=actividad.expira_en,
            activa=actividad.activa,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, actividad: Actividad) -> Actividad:
        stmt = select(ActividadModel).where(ActividadModel.id == actividad.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Actividad con ID {actividad.id} no encontrada")

        model.titulo = actividad.titulo
        model.descripcion = actividad.descripcion
        model.modo = actividad.modo
        model.pares = actividad.pares
        model.configuracion = actividad.configuracion
        model.paciente_id = actividad.paciente_id
        model.tipo_plantilla = actividad.tipo_plantilla
        model.token_acceso = actividad.token_acceso
        model.expira_en = actividad.expira_en
        model.activa = actividad.activa
        if actividad.eliminado_en:
            model.eliminado_en = actividad.eliminado_en

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, actividad_id: UUID) -> bool:
        stmt = select(ActividadModel).where(ActividadModel.id == actividad_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.eliminado_en = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.flush()
        return True
