from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.application.dtos.auth import (
    RegisterRequestDTO,
    RegisterResponseDTO,
    LoginRequestDTO,
    LoginResponseDTO,
    RefreshTokenRequestDTO,
    RefreshTokenResponseDTO,
    LogoutRequestDTO,
    MessageResponseDTO,
    ProfesionalResponseDTO,
    GoogleAuthRequestDTO,
)
from app.application.use_cases import (
    RegisterProfesionalUseCase,
    LoginProfesionalUseCase,
    RefreshTokenUseCase,
    LogoutProfesionalUseCase,
    AuthenticateGoogleUseCase,
)
from app.domain.exceptions import (
    ProfesionalAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    GoogleAuthException,
)
from app.domain.models.profesional import Profesional
from app.infrastructure.oauth.google_client import GoogleOAuthClient
from app.presentation.api.v1.dependencies import (
    get_register_use_case,
    get_login_use_case,
    get_refresh_token_use_case,
    get_logout_use_case,
    get_authenticate_google_use_case,
    get_google_client,
    get_current_user,
)

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=RegisterResponseDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
    summary="Registrar un nuevo profesional",
    description="Crea una nueva cuenta de profesional validando email único, contraseña robusta (min 8 chars, mayúscula, número, símbolo) y confirmación idéntica. Hashea la clave con bcrypt (rounds=12) y devuelve los tokens JWT de acceso y refresco."
)
async def register(
    dto: RegisterRequestDTO,
    use_case: Annotated[RegisterProfesionalUseCase, Depends(get_register_use_case)]
) -> Any:
    logger.info(f"Intento de registro para: {dto.email}")
    try:
        response = await use_case.execute(dto)
        logger.info(f"Registro exitoso para: {dto.email} con ID: {response.id}")
        return response
    except ProfesionalAlreadyExistsException as e:
        logger.warning(f"Conflicto de registro - Email ya existe: {dto.email}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
    tags=["Auth"],
    summary="Iniciar sesión con email y contraseña",
    description="Autentica a un profesional contra la base de datos verificando el hash bcrypt. Devuelve un access_token (30 min), refresh_token (7 días), expires_in y el perfil del usuario autenticado."
)
async def login(
    dto: LoginRequestDTO,
    use_case: Annotated[LoginProfesionalUseCase, Depends(get_login_use_case)]
) -> Any:
    logger.info(f"Intento de inicio de sesión para: {dto.email}")
    try:
        response = await use_case.execute(dto)
        logger.info(f"Inicio de sesión exitoso para: {dto.email}")
        return response
    except InvalidCredentialsException as e:
        logger.warning(f"Credenciales inválidas para: {dto.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/login/form",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
    tags=["Auth"],
    summary="Login compatible con Swagger OAuth2 (Form Data)",
    description="Endpoint auxiliar para la ventana de autenticación integrada de Swagger UI.",
    include_in_schema=False
)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[LoginProfesionalUseCase, Depends(get_login_use_case)]
) -> Any:
    dto = LoginRequestDTO(email=form_data.username, password=form_data.password)
    try:
        return await use_case.execute(dto)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponseDTO,
    status_code=status.HTTP_200_OK,
    tags=["Auth"],
    summary="Renovar access token mediante refresh token",
    description="Recibe un refresh token JWT válido y no revocado, y genera un nuevo access token de corta duración sin requerir que el usuario reingrese sus credenciales."
)
async def refresh_token(
    dto: RefreshTokenRequestDTO,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)]
) -> Any:
    logger.info("Solicitud de renovación de token recibida")
    try:
        response = await use_case.execute(dto)
        return response
    except InvalidTokenException as e:
        logger.warning(f"Fallo al renovar token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/logout",
    response_model=MessageResponseDTO,
    status_code=status.HTTP_200_OK,
    tags=["Auth"],
    summary="Cerrar sesión e invalidar refresh token",
    description="Invalida el refresh token del profesional añadiéndolo a la blacklist en memoria, impidiendo que pueda ser reutilizado para renovar sesiones."
)
async def logout(
    dto: LogoutRequestDTO,
    use_case: Annotated[LogoutProfesionalUseCase, Depends(get_logout_use_case)]
) -> Any:
    logger.info("Solicitud de cierre de sesión recibida")
    try:
        response = await use_case.execute(dto)
        logger.info("Sesión cerrada correctamente")
        return response
    except InvalidTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/me",
    response_model=ProfesionalResponseDTO,
    status_code=status.HTTP_200_OK,
    tags=["Profesionales"],
    summary="Obtener perfil del profesional autenticado",
    description="Ruta protegida que requiere un token JWT Bearer válido. Devuelve los datos del perfil del profesional autenticado (id, email, creado_en)."
)
async def get_me(
    current_user: Annotated[Profesional, Depends(get_current_user)]
) -> Any:
    logger.info(f"Consulta de perfil para profesional ID: {current_user.id}")
    return ProfesionalResponseDTO.model_validate(current_user)


@router.get(
    "/google/login",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    tags=["Auth"],
    summary="Redirige a la pantalla de consentimiento de Google OAuth2",
    description="Genera la URL de autorización de Google OAuth 2.0 y redirige al navegador del usuario para que seleccione su cuenta de Google."
)
async def google_login(
    state: str = Query("", description="Estado CSRF opcional"),
    google_client: Annotated[GoogleOAuthClient, Depends(get_google_client)] = None
) -> Any:
    auth_url = google_client.get_authorization_url(state=state)
    logger.info(f"Redirigiendo a pantalla de autenticación de Google")
    return RedirectResponse(url=auth_url)


@router.get(
    "/google/callback",
    status_code=status.HTTP_200_OK,
    tags=["Auth"],
    summary="Recibe código de Google, crea/actualiza profesional y devuelve JWT",
    description="Endpoint de callback que recibe el 'code' emitido por Google, lo intercambia por tokens, valida el email del usuario, registra automáticamente al profesional si no existía y emite los tokens JWT de Vinculia."
)
async def google_callback(
    code: str = Query(..., description="Código de autorización devuelto por Google"),
    google_client: Annotated[GoogleOAuthClient, Depends(get_google_client)] = None,
    use_case: Annotated[AuthenticateGoogleUseCase, Depends(get_authenticate_google_use_case)] = None,
) -> Any:
    logger.info("Callback de Google OAuth recibido")
    try:
        user_info = await google_client.exchange_code_for_tokens(code)
        tokens = await use_case.execute(GoogleAuthRequestDTO(id_token=f"mock-google-token-{user_info['email']}"))
        return tokens
    except GoogleAuthException as e:
        logger.error(f"Error en callback de Google: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
