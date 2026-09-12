from uuid import UUID
from app.domain.exceptions import ProfesionalNotFoundException
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort


class GetCurrentProfesionalUseCase:
    """Caso de uso para consultar el perfil del profesional autenticado."""

    def __init__(self, repository: ProfesionalRepositoryPort):
        self.repository = repository

    async def execute(self, profesional_id: UUID) -> Profesional:
        profesional = await self.repository.get_by_id(profesional_id)
        if not profesional:
            raise ProfesionalNotFoundException(str(profesional_id))
        return profesional
