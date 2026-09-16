from uuid import UUID
from typing import List, Tuple
from app.domain.models.paciente import Paciente
from app.domain.ports.paciente_repository import PacienteRepositoryPort
from app.domain.exceptions import PacienteNotFoundException
from app.application.dtos.paciente import PacienteCreateDTO, PacienteUpdateDTO


class CreatePacienteUseCase:
    def __init__(self, repo: PacienteRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, dto: PacienteCreateDTO) -> Paciente:
        paciente = Paciente(
            profesional_id=profesional_id,
            apodo=dto.apodo.strip(),
            edad=dto.edad,
        )
        return await self.repo.create(paciente)


class ListPacientesUseCase:
    def __init__(self, repo: PacienteRepositoryPort):
        self.repo = repo

    async def execute(
        self, profesional_id: UUID, page: int = 1, size: int = 10
    ) -> Tuple[List[Paciente], int]:
        return await self.repo.list_by_profesional(profesional_id, page=page, size=size)


class GetPacienteUseCase:
    def __init__(self, repo: PacienteRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, paciente_id: UUID) -> Paciente:
        paciente = await self.repo.get_by_id(paciente_id)
        if not paciente or paciente.profesional_id != profesional_id or paciente.eliminado_en is not None:
            raise PacienteNotFoundException(str(paciente_id))
        return paciente


class UpdatePacienteUseCase:
    def __init__(self, repo: PacienteRepositoryPort):
        self.repo = repo

    async def execute(
        self, profesional_id: UUID, paciente_id: UUID, dto: PacienteUpdateDTO
    ) -> Paciente:
        paciente = await self.repo.get_by_id(paciente_id)
        if not paciente or paciente.profesional_id != profesional_id or paciente.eliminado_en is not None:
            raise PacienteNotFoundException(str(paciente_id))

        if dto.apodo is not None:
            paciente.apodo = dto.apodo.strip()
        if dto.edad is not None:
            paciente.edad = dto.edad

        return await self.repo.update(paciente)


class DeletePacienteUseCase:
    def __init__(self, repo: PacienteRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, paciente_id: UUID) -> bool:
        paciente = await self.repo.get_by_id(paciente_id)
        if not paciente or paciente.profesional_id != profesional_id or paciente.eliminado_en is not None:
            raise PacienteNotFoundException(str(paciente_id))

        return await self.repo.delete(paciente_id)
