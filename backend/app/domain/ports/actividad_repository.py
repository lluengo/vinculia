from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, Tuple
from app.domain.models.actividad import Actividad


class ActividadRepositoryPort(ABC):
    """Puerto de repositorio para la entidad Actividad."""

    @abstractmethod
    async def get_by_id(self, actividad_id: UUID) -> Optional[Actividad]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Actividad]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_profesional(
        self,
        profesional_id: UUID,
        paciente_id: Optional[UUID] = None,
        tipo_plantilla: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        include_deleted: bool = False
    ) -> Tuple[List[Actividad], int]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, actividad: Actividad) -> Actividad:
        raise NotImplementedError

    @abstractmethod
    async def update(self, actividad: Actividad) -> Actividad:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, actividad_id: UUID) -> bool:
        raise NotImplementedError
