from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, Tuple
from app.domain.models.paciente import Paciente


class PacienteRepositoryPort(ABC):
    """Puerto de repositorio para la entidad Paciente."""

    @abstractmethod
    async def get_by_id(self, paciente_id: UUID) -> Optional[Paciente]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_profesional(
        self, profesional_id: UUID, page: int = 1, size: int = 10, include_deleted: bool = False
    ) -> Tuple[List[Paciente], int]:
        """Retorna lista de pacientes y total para paginación."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, paciente: Paciente) -> Paciente:
        raise NotImplementedError

    @abstractmethod
    async def update(self, paciente: Paciente) -> Paciente:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, paciente_id: UUID) -> bool:
        """Soft delete de paciente."""
        raise NotImplementedError
