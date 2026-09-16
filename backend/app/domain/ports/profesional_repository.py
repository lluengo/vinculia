from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.models.profesional import Profesional


class ProfesionalRepositoryPort(ABC):
    """Puerto de repositorio para la entidad Profesional."""

    @abstractmethod
    async def get_by_id(self, profesional_id: UUID) -> Optional[Profesional]:
        """Obtiene un profesional por su identificador UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Profesional]:
        """Obtiene un profesional por su correo electrónico."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, profesional: Profesional) -> Profesional:
        """Persiste un nuevo profesional."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, profesional: Profesional) -> Profesional:
        """Actualiza los datos de un profesional existente."""
        raise NotImplementedError
