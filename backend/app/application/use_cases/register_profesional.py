import uuid
from app.application.dtos.auth import RegisterRequestDTO, RegisterResponseDTO
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.domain.exceptions import ProfesionalAlreadyExistsException
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort


class RegisterProfesionalUseCase:
    """Caso de uso para registrar un nuevo profesional."""

    def __init__(self, repository: ProfesionalRepositoryPort):
        self.repository = repository

    async def execute(self, dto: RegisterRequestDTO) -> RegisterResponseDTO:
        normalized_email = dto.email.lower().strip()
        existing = await self.repository.get_by_email(normalized_email)
        if existing:
            raise ProfesionalAlreadyExistsException(normalized_email)

        hashed_pwd = hash_password(dto.password)
        new_profesional = Profesional(
            id=uuid.uuid4(),
            email=normalized_email,
            password_hash=hashed_pwd,
        )

        created_profesional = await self.repository.create(new_profesional)

        access_token = create_access_token(subject=created_profesional.id)
        refresh_token = create_refresh_token(subject=created_profesional.id)

        return RegisterResponseDTO(
            id=created_profesional.id,
            email=created_profesional.email,
            creado_en=created_profesional.creado_en,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
