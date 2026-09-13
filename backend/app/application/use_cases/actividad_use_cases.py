import secrets
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Dict, Any

from app.domain.models.actividad import Actividad
from app.domain.ports.actividad_repository import ActividadRepositoryPort
from app.domain.ports.paciente_repository import PacienteRepositoryPort
from app.domain.exceptions import (
    ActividadNotFoundException,
    TokenInvalidoException,
    ActividadInvalidaException,
)
from app.application.dtos.actividad import (
    ActividadCreateDTO,
    ActividadUpdateDTO,
    ActividadPublicaResponseDTO,
)


class CreateActividadUseCase:
    def __init__(self, repo: ActividadRepositoryPort, paciente_repo: Optional[PacienteRepositoryPort] = None):
        self.repo = repo
        self.paciente_repo = paciente_repo

    async def execute(self, profesional_id: UUID, dto: ActividadCreateDTO) -> Actividad:
        valid_modes = {"imagen-imagen", "imagen-sonido", "texto-imagen"}
        if dto.modo not in valid_modes:
            raise ActividadInvalidaException(f"Modo '{dto.modo}' no válido. Opciones: {', '.join(valid_modes)}")

        if dto.paciente_id and self.paciente_repo:
            paciente = await self.paciente_repo.get_by_id(dto.paciente_id)
            if not paciente or paciente.profesional_id != profesional_id:
                raise ActividadInvalidaException("El paciente especificado no existe o no pertenece al profesional.")

        pares_dict = [p.model_dump() for p in dto.pares]
        config_dict = dto.configuracion.model_dump() if dto.configuracion else {}

        actividad = Actividad(
            profesional_id=profesional_id,
            paciente_id=dto.paciente_id,
            tipo_plantilla=dto.tipo_plantilla,
            titulo=dto.titulo.strip(),
            descripcion=dto.descripcion.strip() if dto.descripcion else None,
            modo=dto.modo,
            pares=pares_dict,
            configuracion=config_dict,
        )
        return await self.repo.create(actividad)


class ListActividadesUseCase:
    def __init__(self, repo: ActividadRepositoryPort):
        self.repo = repo

    async def execute(
        self,
        profesional_id: UUID,
        paciente_id: Optional[UUID] = None,
        tipo_plantilla: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> Tuple[List[Actividad], int]:
        return await self.repo.list_by_profesional(
            profesional_id=profesional_id,
            paciente_id=paciente_id,
            tipo_plantilla=tipo_plantilla,
            page=page,
            size=size,
        )


class GetActividadUseCase:
    def __init__(self, repo: ActividadRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, actividad_id: UUID) -> Actividad:
        actividad = await self.repo.get_by_id(actividad_id)
        if not actividad or actividad.profesional_id != profesional_id or actividad.eliminado_en is not None:
            raise ActividadNotFoundException(str(actividad_id))
        return actividad


class UpdateActividadUseCase:
    def __init__(self, repo: ActividadRepositoryPort, paciente_repo: Optional[PacienteRepositoryPort] = None):
        self.repo = repo
        self.paciente_repo = paciente_repo

    async def execute(
        self, profesional_id: UUID, actividad_id: UUID, dto: ActividadUpdateDTO
    ) -> Actividad:
        actividad = await self.repo.get_by_id(actividad_id)
        if not actividad or actividad.profesional_id != profesional_id or actividad.eliminado_en is not None:
            raise ActividadNotFoundException(str(actividad_id))

        if dto.paciente_id is not None:
            if self.paciente_repo:
                paciente = await self.paciente_repo.get_by_id(dto.paciente_id)
                if not paciente or paciente.profesional_id != profesional_id:
                    raise ActividadInvalidaException("El paciente especificado no existe.")
            actividad.paciente_id = dto.paciente_id

        if dto.titulo is not None:
            actividad.titulo = dto.titulo.strip()
        if dto.descripcion is not None:
            actividad.descripcion = dto.descripcion.strip()
        if dto.modo is not None:
            actividad.modo = dto.modo
        if dto.pares is not None:
            actividad.pares = [p.model_dump() for p in dto.pares]
        if dto.configuracion is not None:
            actividad.configuracion = dto.configuracion.model_dump()
        if dto.activa is not None:
            actividad.activa = dto.activa
        if dto.tipo_plantilla is not None:
            actividad.tipo_plantilla = dto.tipo_plantilla

        return await self.repo.update(actividad)


class DeleteActividadUseCase:
    def __init__(self, repo: ActividadRepositoryPort):
        self.repo = repo

    async def execute(self, profesional_id: UUID, actividad_id: UUID) -> bool:
        actividad = await self.repo.get_by_id(actividad_id)
        if not actividad or actividad.profesional_id != profesional_id or actividad.eliminado_en is not None:
            raise ActividadNotFoundException(str(actividad_id))
        return await self.repo.delete(actividad_id)


class GenerarEnlaceUseCase:
    def __init__(self, repo: ActividadRepositoryPort, expiration_days: int = 7):
        self.repo = repo
        self.expiration_days = expiration_days

    async def execute(self, profesional_id: UUID, actividad_id: UUID) -> Tuple[str, datetime]:
        actividad = await self.repo.get_by_id(actividad_id)
        if not actividad or actividad.profesional_id != profesional_id or actividad.eliminado_en is not None:
            raise ActividadNotFoundException(str(actividad_id))

        token = secrets.token_urlsafe(32)
        expira_en = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=self.expiration_days)

        actividad.token_acceso = token
        actividad.expira_en = expira_en
        actividad.activa = True

        await self.repo.update(actividad)
        return token, expira_en


class GetActividadPublicaUseCase:
    def __init__(self, repo: ActividadRepositoryPort, paciente_repo: Optional[PacienteRepositoryPort] = None):
        self.repo = repo
        self.paciente_repo = paciente_repo

    async def execute(self, token: str) -> ActividadPublicaResponseDTO:
        actividad = await self.repo.get_by_token(token)
        if not actividad or not actividad.activa:
            raise TokenInvalidoException("El enlace de actividad no es válido o ha sido desactivado.")

        if actividad.expira_en and actividad.expira_en < datetime.now(timezone.utc).replace(tzinfo=None):
            raise TokenInvalidoException("El enlace de la actividad ha expirado.")

        apodo_paciente = None
        if actividad.paciente_id and self.paciente_repo:
            paciente = await self.paciente_repo.get_by_id(actividad.paciente_id)
            if paciente:
                apodo_paciente = paciente.apodo

        return ActividadPublicaResponseDTO(
            id=actividad.id,
            titulo=actividad.titulo,
            descripcion=actividad.descripcion,
            modo=actividad.modo,
            pares=actividad.pares,
            configuracion=actividad.configuracion,
            apodo_paciente=apodo_paciente,
        )
