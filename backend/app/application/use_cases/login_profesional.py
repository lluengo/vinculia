from app.application.dtos.auth import LoginRequestDTO, LoginResponseDTO, ProfesionalResponseDTO
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.domain.exceptions import InvalidCredentialsException
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort


class LoginProfesionalUseCase:
    """Caso de uso para autenticar un profesional existente."""

    def __init__(self, repository: ProfesionalRepositoryPort):
        self.repository = repository

    async def execute(self, dto: LoginRequestDTO) -> LoginResponseDTO:
        normalized_email = dto.email.lower().strip()
        profesional = await self.repository.get_by_email(normalized_email)
        
        if not profesional:
            raise InvalidCredentialsException("Credenciales inválidas.")

        if not verify_password(dto.password, profesional.password_hash):
            raise InvalidCredentialsException("Credenciales inválidas.")

        access_token = create_access_token(subject=profesional.id)
        refresh_token = create_refresh_token(subject=profesional.id)

        return LoginResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=ProfesionalResponseDTO.model_validate(profesional),
        )
