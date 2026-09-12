from uuid import UUID
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.domain.models.profesional import Profesional
from app.domain.ports.profesional_repository import ProfesionalRepositoryPort
from app.domain.exceptions import InvalidTokenException, DomainException
from app.infrastructure.db.repositories.sql_profesional_repository import SqlProfesionalRepository
from app.infrastructure.oauth.google_client import GoogleOAuthClient
from app.application.use_cases import (
    RegisterProfesionalUseCase,
    LoginProfesionalUseCase,
    RefreshTokenUseCase,
    GetCurrentProfesionalUseCase,
    AuthenticateGoogleUseCase,
    LogoutProfesionalUseCase,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/form",
    auto_error=False
)


def get_profesional_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ProfesionalRepositoryPort:
    return SqlProfesionalRepository(session)


def get_google_client() -> GoogleOAuthClient:
    return GoogleOAuthClient()


def get_register_use_case(
    repo: Annotated[ProfesionalRepositoryPort, Depends(get_profesional_repository)]
) -> RegisterProfesionalUseCase:
    return RegisterProfesionalUseCase(repo)


def get_login_use_case(
    repo: Annotated[ProfesionalRepositoryPort, Depends(get_profesional_repository)]
) -> LoginProfesionalUseCase:
    return LoginProfesionalUseCase(repo)


def get_refresh_token_use_case(
    repo: Annotated[ProfesionalRepositoryPort, Depends(get_profesional_repository)]
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(repo)


def get_logout_use_case() -> LogoutProfesionalUseCase:
    return LogoutProfesionalUseCase()


def get_current_profesional_use_case(
    repo: Annotated[ProfesionalRepositoryPort, Depends(get_profesional_repository)]
) -> GetCurrentProfesionalUseCase:
    return GetCurrentProfesionalUseCase(repo)


def get_authenticate_google_use_case(
    repo: Annotated[ProfesionalRepositoryPort, Depends(get_profesional_repository)],
    google_client: Annotated[GoogleOAuthClient, Depends(get_google_client)]
) -> AuthenticateGoogleUseCase:
    return AuthenticateGoogleUseCase(repo, google_client)


async def get_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    use_case: Annotated[GetCurrentProfesionalUseCase, Depends(get_current_profesional_use_case)]
) -> Profesional:
    """Extrae el token Bearer (Swagger o frontend), lo valida y obtiene el Profesional autenticado."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Token no provisto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token, expected_type="access")
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene identificador de sujeto válido.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        profesional_id = UUID(sub)
    except (InvalidTokenException, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await use_case.execute(profesional_id)
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
