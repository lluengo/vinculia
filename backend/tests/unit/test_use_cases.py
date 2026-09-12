import uuid
from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from app.application.dtos.auth import (
    RegisterRequestDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    LogoutRequestDTO,
    GoogleAuthRequestDTO,
)
from app.application.use_cases import (
    RegisterProfesionalUseCase,
    LoginProfesionalUseCase,
    RefreshTokenUseCase,
    GetCurrentProfesionalUseCase,
    AuthenticateGoogleUseCase,
    LogoutProfesionalUseCase,
)
from app.core.security import hash_password, create_refresh_token, decode_token
from app.domain.exceptions import (
    ProfesionalAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    ProfesionalNotFoundException,
)
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort
from app.infrastructure.oauth.google_client import GoogleOAuthClient


def test_register_dto_weak_password():
    # Sin mayúscula
    with pytest.raises(ValidationError):
        RegisterRequestDTO(email="test@vinculia.com", password="password123!", password_confirm="password123!")
    # Sin número
    with pytest.raises(ValidationError):
        RegisterRequestDTO(email="test@vinculia.com", password="Password!", password_confirm="Password!")
    # Sin símbolo
    with pytest.raises(ValidationError):
        RegisterRequestDTO(email="test@vinculia.com", password="Password123", password_confirm="Password123")
    # Menos de 8 caracteres
    with pytest.raises(ValidationError):
        RegisterRequestDTO(email="test@vinculia.com", password="P1!", password_confirm="P1!")
    # Contraseñas no coinciden
    with pytest.raises(ValidationError):
        RegisterRequestDTO(email="test@vinculia.com", password="Password123!", password_confirm="Different123!")


@pytest.mark.asyncio
async def test_register_profesional_success():
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = None
    
    def mock_create(profesional: Profesional):
        return profesional
    repo.create.side_effect = mock_create

    use_case = RegisterProfesionalUseCase(repo)
    dto = RegisterRequestDTO(
        email="psico@vinculia.com",
        password="Password123!",
        password_confirm="Password123!"
    )

    response = await use_case.execute(dto)

    assert response.email == "psico@vinculia.com"
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.token_type == "bearer"
    repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_profesional_already_exists():
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = Profesional(
        id=uuid.uuid4(),
        email="psico@vinculia.com",
        password_hash="somehash"
    )

    use_case = RegisterProfesionalUseCase(repo)
    dto = RegisterRequestDTO(
        email="psico@vinculia.com",
        password="Password123!",
        password_confirm="Password123!"
    )

    with pytest.raises(ProfesionalAlreadyExistsException):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_login_profesional_success():
    plain_password = "Password123!"
    hashed = hash_password(plain_password)
    profesional_id = uuid.uuid4()

    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = Profesional(
        id=profesional_id,
        email="fono@vinculia.com",
        password_hash=hashed
    )

    use_case = LoginProfesionalUseCase(repo)
    dto = LoginRequestDTO(email="fono@vinculia.com", password=plain_password)

    response = await use_case.execute(dto)

    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.expires_in == 1800
    assert response.user.email == "fono@vinculia.com"


@pytest.mark.asyncio
async def test_login_profesional_invalid_password():
    hashed = hash_password("CorrectPassword123!")
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = Profesional(
        id=uuid.uuid4(),
        email="fono@vinculia.com",
        password_hash=hashed
    )

    use_case = LoginProfesionalUseCase(repo)
    dto = LoginRequestDTO(email="fono@vinculia.com", password="WrongPassword123!")

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_login_profesional_not_found():
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = None

    use_case = LoginProfesionalUseCase(repo)
    dto = LoginRequestDTO(email="unknown@vinculia.com", password="Password123!")

    with pytest.raises(InvalidCredentialsException):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_refresh_token_success():
    profesional_id = uuid.uuid4()
    refresh_token = create_refresh_token(subject=profesional_id)

    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_id.return_value = Profesional(
        id=profesional_id,
        email="pro@vinculia.com",
        password_hash="hash"
    )

    use_case = RefreshTokenUseCase(repo)
    dto = RefreshTokenRequestDTO(refresh_token=refresh_token)

    response = await use_case.execute(dto)

    assert response.access_token is not None
    assert response.token_type == "bearer"
    assert response.expires_in == 1800


@pytest.mark.asyncio
async def test_refresh_token_user_deleted():
    profesional_id = uuid.uuid4()
    refresh_token = create_refresh_token(subject=profesional_id)

    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_id.return_value = None

    use_case = RefreshTokenUseCase(repo)
    dto = RefreshTokenRequestDTO(refresh_token=refresh_token)

    with pytest.raises(InvalidTokenException):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_logout_use_case():
    profesional_id = uuid.uuid4()
    refresh_token = create_refresh_token(subject=profesional_id)

    use_case = LogoutProfesionalUseCase()
    dto = LogoutRequestDTO(refresh_token=refresh_token)

    res = await use_case.execute(dto)
    assert "exitosa" in res.message or "revocado" in res.message

    # Verificar que el token revocado ya no sea válido
    with pytest.raises(InvalidTokenException) as exc_info:
        decode_token(refresh_token)
    assert "revocado" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_current_profesional_success():
    profesional_id = uuid.uuid4()
    expected_profesional = Profesional(
        id=profesional_id,
        email="pro@vinculia.com",
        password_hash="hash"
    )

    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_id.return_value = expected_profesional

    use_case = GetCurrentProfesionalUseCase(repo)
    result = await use_case.execute(profesional_id)

    assert result.id == profesional_id
    assert result.email == "pro@vinculia.com"


@pytest.mark.asyncio
async def test_get_current_profesional_not_found():
    profesional_id = uuid.uuid4()
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_id.return_value = None

    use_case = GetCurrentProfesionalUseCase(repo)

    with pytest.raises(ProfesionalNotFoundException):
        await use_case.execute(profesional_id)


@pytest.mark.asyncio
async def test_authenticate_google_existing_user():
    email = "google_user@vinculia.com"
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = Profesional(
        id=uuid.uuid4(),
        email=email,
        password_hash="hash"
    )

    google_client = AsyncMock(spec=GoogleOAuthClient)
    google_client.verify_id_token.return_value = {"email": email}

    use_case = AuthenticateGoogleUseCase(repo, google_client)
    dto = GoogleAuthRequestDTO(id_token="mock-google-token-google_user@vinculia.com")

    tokens = await use_case.execute(dto)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_authenticate_google_new_user_auto_register():
    email = "new_google_user@vinculia.com"
    repo = AsyncMock(spec=ProfesionalRepositoryPort)
    repo.get_by_email.return_value = None

    def mock_create(profesional: Profesional):
        return profesional
    repo.create.side_effect = mock_create

    google_client = AsyncMock(spec=GoogleOAuthClient)
    google_client.verify_id_token.return_value = {"email": email}

    use_case = AuthenticateGoogleUseCase(repo, google_client)
    dto = GoogleAuthRequestDTO(id_token="mock-google-token-new_google_user@vinculia.com")

    tokens = await use_case.execute(dto)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    repo.create.assert_awaited_once()
