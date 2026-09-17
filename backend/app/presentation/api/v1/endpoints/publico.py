from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func
from app.core.database import get_db
from app.domain.exceptions import TokenInvalidoException
from app.infrastructure.db.models.sesion_juego import SesionJuegoModel
from app.infrastructure.db.repositories.sql_actividad_repository import SqlActividadRepository
from app.application.dtos.actividad import (
    ActividadPublicaResponseDTO,
    SesionPublicaCreateDTO,
)
from app.application.use_cases import GetActividadPublicaUseCase
from app.presentation.api.v1.dependencies import get_actividad_publica_use_case

router = APIRouter(prefix="/publico", tags=["Público"])


@router.get("/actividades/{token}", response_model=ActividadPublicaResponseDTO)
async def get_actividad_publica(
    token: str,
    use_case: Annotated[GetActividadPublicaUseCase, Depends(get_actividad_publica_use_case)],
):
    try:
        return await use_case.execute(token)
    except TokenInvalidoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/sesiones", status_code=status.HTTP_201_CREATED)
async def registrar_sesion_publica(
    dto: SesionPublicaCreateDTO,
    session: Annotated[AsyncSession, Depends(get_db)],
    use_case: Annotated[GetActividadPublicaUseCase, Depends(get_actividad_publica_use_case)],
):
    paciente_id = None
    if dto.token:
        try:
            actividad_repo = SqlActividadRepository(session)
            act_entity = await actividad_repo.get_by_token(dto.token)
            if act_entity:
                actividad_id = act_entity.id
                paciente_id = act_entity.paciente_id
        except Exception:
            pass
    elif actividad_id:
        actividad_repo = SqlActividadRepository(session)
        act_entity = await actividad_repo.get_by_id(actividad_id)
        if act_entity:
            paciente_id = act_entity.paciente_id

    sesion_model = SesionJuegoModel(
        actividad_id=actividad_id,
        paciente_id=paciente_id,
        tiempo_segundos=dto.tiempo_segundos,
        aciertos=dto.aciertos,
        errores=dto.errores,
    )
    session.add(sesion_model)

    # Actualizar fecha de última sesión en el paciente si existe
    if paciente_id:
        from app.infrastructure.db.models.paciente import PacienteModel
        from sqlalchemy import update
        await session.execute(
            update(PacienteModel)
            .where(PacienteModel.id == paciente_id)
            .values(ultima_sesion=func.now())
        )

    await session.commit()
    return {"message": "Sesión registrada exitosamente", "id": str(sesion_model.id)}
