from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import UUID
import bcrypt
import jwt
from app.core.config import settings
from app.domain.exceptions import InvalidTokenException


def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro con factor de coste rounds=12."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash guardado."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Genera un JWT access token de corta duración."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Genera un JWT refresh token de larga duración."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Blacklist de tokens en memoria
_revoked_tokens: set[str] = set()


def revoke_token(token: str) -> None:
    """Añade un token a la lista negra de tokens revocados."""
    _revoked_tokens.add(token.strip())


def is_token_revoked(token: str) -> bool:
    """Comprueba si un token ha sido revocado."""
    return token.strip() in _revoked_tokens


def decode_token(token: str, expected_type: Optional[str] = None) -> dict[str, Any]:
    """Decodifica y valida un token JWT."""
    if is_token_revoked(token):
        raise InvalidTokenException("El token ha sido revocado (sesión cerrada).")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if expected_type and payload.get("type") != expected_type:
            raise InvalidTokenException(f"Tipo de token inválido. Se esperaba '{expected_type}'.")
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException("El token ha expirado.")
    except jwt.PyJWTError as e:
        raise InvalidTokenException(f"Token no válido: {str(e)}")
