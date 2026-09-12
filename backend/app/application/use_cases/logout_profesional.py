from app.application.dtos.auth import LogoutRequestDTO, MessageResponseDTO
from app.core.security import decode_token, revoke_token


class LogoutProfesionalUseCase:
    """Caso de uso para cerrar sesión e invalidar el refresh token."""

    async def execute(self, dto: LogoutRequestDTO) -> MessageResponseDTO:
        # Validar que el token sea un refresh token válido antes de revocarlo
        decode_token(dto.refresh_token, expected_type="refresh")
        revoke_token(dto.refresh_token)
        return MessageResponseDTO(message="Sesión cerrada exitosamente. Token revocado.")
