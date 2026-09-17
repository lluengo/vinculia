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
from app.domain.ports.paciente_repository import PacienteRepositoryPort
from app.domain.ports.actividad_repository import ActividadRepositoryPort
from app.infrastructure.db.repositories.sql_paciente_repository import SqlPacienteRepository
from app.infrastructure.db.repositories.sql_actividad_repository import SqlActividadRepository
from app.domain.ports.metrica_repository import MetricaRepositoryPort
from app.infrastructure.db.repositories.sql_metrica_repository import SqlMetricaRepository
from app.application.use_cases import (
    RegisterProfesionalUseCase,
    LoginProfesionalUseCase,
    RefreshTokenUseCase,
    GetCurrentProfesionalUseCase,
    AuthenticateGoogleUseCase,
    LogoutProfesionalUseCase,
    CreatePacienteUseCase,
    ListPacientesUseCase,
    GetPacienteUseCase,
    UpdatePacienteUseCase,
    DeletePacienteUseCase,
    CreateActividadUseCase,
    ListActividadesUseCase,
    GetActividadUseCase,
    UpdateActividadUseCase,
    DeleteActividadUseCase,
    GenerarEnlaceUseCase,
    GetActividadPublicaUseCase,
    GetPacienteResumenMetricasUseCase,
    GetPacienteEvolucionUseCase,
    GetPacientePorActividadUseCase,
    ExportarSesionesPacienteUseCase,
    GetGlobalResumenUseCase,
    GetRankingPacientesUseCase,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/form",
    auto_error=False
)


def get_profesional_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ProfesionalRepositoryPort:
    return SqlProfesionalRepository(session)


def get_paciente_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> PacienteRepositoryPort:
    return SqlPacienteRepository(session)


def get_actividad_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ActividadRepositoryPort:
    return SqlActividadRepository(session)


def get_create_paciente_use_case(
    repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)]
) -> CreatePacienteUseCase:
    return CreatePacienteUseCase(repo)


def get_list_pacientes_use_case(
    repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)]
) -> ListPacientesUseCase:
    return ListPacientesUseCase(repo)


def get_paciente_use_case(
    repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)]
) -> GetPacienteUseCase:
    return GetPacienteUseCase(repo)


def get_update_paciente_use_case(
    repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)]
) -> UpdatePacienteUseCase:
    return UpdatePacienteUseCase(repo)


def get_delete_paciente_use_case(
    repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)]
) -> DeletePacienteUseCase:
    return DeletePacienteUseCase(repo)


def get_create_actividad_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)],
    paciente_repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)],
) -> CreateActividadUseCase:
    return CreateActividadUseCase(repo, paciente_repo)


def get_list_actividades_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)]
) -> ListActividadesUseCase:
    return ListActividadesUseCase(repo)


def get_actividad_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)]
) -> GetActividadUseCase:
    return GetActividadUseCase(repo)


def get_update_actividad_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)],
    paciente_repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)],
) -> UpdateActividadUseCase:
    return UpdateActividadUseCase(repo, paciente_repo)


def get_delete_actividad_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)]
) -> DeleteActividadUseCase:
    return DeleteActividadUseCase(repo)


def get_generar_enlace_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)]
) -> GenerarEnlaceUseCase:
    return GenerarEnlaceUseCase(repo)


def get_actividad_publica_use_case(
    repo: Annotated[ActividadRepositoryPort, Depends(get_actividad_repository)],
    paciente_repo: Annotated[PacienteRepositoryPort, Depends(get_paciente_repository)],
) -> GetActividadPublicaUseCase:
    return GetActividadPublicaUseCase(repo, paciente_repo)


def get_metrica_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> MetricaRepositoryPort:
    return SqlMetricaRepository(session)


def get_paciente_resumen_metricas_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> GetPacienteResumenMetricasUseCase:
    return GetPacienteResumenMetricasUseCase(repo)


def get_paciente_evolucion_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> GetPacienteEvolucionUseCase:
    return GetPacienteEvolucionUseCase(repo)


def get_paciente_por_actividad_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> GetPacientePorActividadUseCase:
    return GetPacientePorActividadUseCase(repo)


def get_exportar_sesiones_paciente_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> ExportarSesionesPacienteUseCase:
    return ExportarSesionesPacienteUseCase(repo)


def get_global_resumen_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> GetGlobalResumenUseCase:
    return GetGlobalResumenUseCase(repo)


def get_ranking_pacientes_use_case(
    repo: Annotated[MetricaRepositoryPort, Depends(get_metrica_repository)]
) -> GetRankingPacientesUseCase:
    return GetRankingPacientesUseCase(repo)



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
