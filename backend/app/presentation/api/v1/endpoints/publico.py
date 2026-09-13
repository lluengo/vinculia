from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.exceptions import TokenInvalidoException
from app.infrastructure.db.models.sesion_juego import SesionJuegoModel
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
    actividad_id = dto.actividad_id
    if not actividad_id and dto.token:
        try:
            actividad = await use_case.execute(dto.token)
            actividad_id = actividad.id
        except TokenInvalidoException:
            pass

    sesion_model = SesionJuegoModel(
        actividad_id=actividad_id,
        tiempo_segundos=dto.tiempo_segundos,
        aciertos=dto.aciertos,
        errores=dto.errores,
    )
    session.add(sesion_model)
    await session.commit()
    return {"message": "Sesión registrada exitosamente", "id": str(sesion_model.id)}
