import uuid
import secrets
from app.application.dtos.auth import GoogleAuthRequestDTO, TokenResponseDTO
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort
from app.infrastructure.oauth.google_client import GoogleOAuthClient


class AuthenticateGoogleUseCase:
    """Caso de uso para autenticar o registrar un profesional a través de Google OAuth."""

    def __init__(
        self,
        repository: ProfesionalRepositoryPort,
        google_client: GoogleOAuthClient
    ):
        self.repository = repository
        self.google_client = google_client

    async def execute(self, dto: GoogleAuthRequestDTO) -> TokenResponseDTO:
        user_data = await self.google_client.verify_id_token(dto.id_token)
        email = user_data["email"].lower().strip()

        profesional = await self.repository.get_by_email(email)

        if not profesional:
            # Si el profesional no existe, se crea automáticamente
            random_password = secrets.token_urlsafe(32)
            hashed_pwd = hash_password(random_password)
            new_profesional = Profesional(
                id=uuid.uuid4(),
                email=email,
                password_hash=hashed_pwd,
            )
            profesional = await self.repository.create(new_profesional)

        access_token = create_access_token(subject=profesional.id)
        refresh_token = create_refresh_token(subject=profesional.id)

        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
