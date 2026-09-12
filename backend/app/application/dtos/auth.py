import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


class RegisterRequestDTO(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del profesional")
    password: str = Field(..., min_length=8, description="Contraseña de al menos 8 caracteres con mayúscula, número y símbolo")
    password_confirm: str = Field(..., description="Confirmación idéntica de la contraseña")

    @field_validator("password")
    @classmethod
    def validate_strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("La contraseña debe contener al menos un carácter especial/símbolo.")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Las contraseñas no coinciden.")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "psicologa.maria@vinculia.com",
                "password": "Password123!",
                "password_confirm": "Password123!"
            }
        }
    )


class LoginRequestDTO(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del profesional registrado")
    password: str = Field(..., description="Contraseña en texto plano")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "psicologa.maria@vinculia.com",
                "password": "Password123!"
            }
        }
    )


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str = Field(..., description="Token de refresco JWT válido")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh_token_example..."
            }
        }
    )


class LogoutRequestDTO(BaseModel):
    refresh_token: str = Field(..., description="Token de refresco que se añadirá a la lista negra")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh_token_to_revoke..."
            }
        }
    )


class GoogleAuthRequestDTO(BaseModel):
    id_token: str = Field(..., description="ID Token emitido por Google OAuth 2.0")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMyJ9.google_id_token_example..."
            }
        }
    )


class ProfesionalResponseDTO(BaseModel):
    id: UUID = Field(..., description="Identificador único UUID del profesional")
    email: EmailStr = Field(..., description="Correo electrónico del profesional")
    creado_en: Optional[datetime] = Field(None, description="Fecha y hora de creación de la cuenta")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "psicologa.maria@vinculia.com",
                "creado_en": "2026-09-12T17:00:00.000000"
            }
        }
    )


class RegisterResponseDTO(BaseModel):
    id: UUID = Field(..., description="Identificador único del nuevo profesional")
    email: EmailStr = Field(..., description="Correo electrónico registrado")
    creado_en: Optional[datetime] = Field(None, description="Fecha de creación")
    access_token: str = Field(..., description="Token de acceso JWT (30 minutos)")
    refresh_token: str = Field(..., description="Token de refresco JWT (7 días)")
    token_type: str = Field("bearer", description="Tipo de autenticación (bearer)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "psicologa.maria@vinculia.com",
                "creado_en": "2026-09-12T17:00:00.000000",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class LoginResponseDTO(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco JWT")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(1800, description="Tiempo de expiración en segundos (30 min)")
    user: ProfesionalResponseDTO = Field(..., description="Datos del profesional autenticado")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "psicologa.maria@vinculia.com",
                    "creado_en": "2026-09-12T17:00:00.000000"
                }
            }
        }
    )


class RefreshTokenResponseDTO(BaseModel):
    access_token: str = Field(..., description="Nuevo token de acceso JWT")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(1800, description="Tiempo de expiración en segundos (30 min)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class MessageResponseDTO(BaseModel):
    message: str = Field(..., description="Mensaje de confirmación de la operación")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Sesión cerrada exitosamente. Token revocado."
            }
        }
    )


class TokenResponseDTO(BaseModel):
    access_token: str = Field(..., description="Token de acceso")
    refresh_token: str = Field(..., description="Token de refresco")
    token_type: str = Field("bearer", description="Tipo de token")
