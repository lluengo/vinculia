from uuid import UUID
from app.application.dtos.auth import RefreshTokenRequestDTO, RefreshTokenResponseDTO
from app.core.config import settings
from app.core.security import decode_token, create_access_token
from app.domain.exceptions import InvalidTokenException
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort


class RefreshTokenUseCase:
    """Caso de uso para renovar access token a partir de un refresh token válido."""

    def __init__(self, repository: ProfesionalRepositoryPort):
        self.repository = repository

    async def execute(self, dto: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        payload = decode_token(dto.refresh_token, expected_type="refresh")
        subject = payload.get("sub")
        if not subject:
            raise InvalidTokenException("Token inválido: identificador ausente.")

        try:
            profesional_id = UUID(subject)
        except ValueError:
            raise InvalidTokenException("Identificador de usuario inválido en el token.")

        profesional = await self.repository.get_by_id(profesional_id)
        if not profesional:
            raise InvalidTokenException("El usuario asociado al token no existe o ha sido eliminado.")

        new_access_token = create_access_token(subject=profesional.id)

        return RefreshTokenResponseDTO(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
