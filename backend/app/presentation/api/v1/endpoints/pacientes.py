from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domain.models.profesional import Profesional
from app.domain.exceptions import PacienteNotFoundException, DomainException
from app.application.dtos.paciente import (
    PacienteCreateDTO,
    PacienteUpdateDTO,
    PacienteResponseDTO,
    PacienteListResponseDTO,
)
from app.application.use_cases import (
    CreatePacienteUseCase,
    ListPacientesUseCase,
    GetPacienteUseCase,
    UpdatePacienteUseCase,
    DeletePacienteUseCase,
)
from app.presentation.api.v1.dependencies import (
    get_current_user,
    get_create_paciente_use_case,
    get_list_pacientes_use_case,
    get_paciente_use_case,
    get_update_paciente_use_case,
    get_delete_paciente_use_case,
)

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("", response_model=PacienteResponseDTO, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PacienteResponseDTO, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_paciente(
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[CreatePacienteUseCase, Depends(get_create_paciente_use_case)],
    dto: PacienteCreateDTO,
):
    try:
        paciente = await use_case.execute(current_user.id, dto)
        return paciente
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=PacienteListResponseDTO)
@router.get("/", response_model=PacienteListResponseDTO, include_in_schema=False)
async def list_pacientes(

    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[ListPacientesUseCase, Depends(get_list_pacientes_use_case)],
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
):
    items, total = await use_case.execute(current_user.id, page=page, size=size)
    return PacienteListResponseDTO(
        items=[PacienteResponseDTO.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{id}", response_model=PacienteResponseDTO)
async def get_paciente(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetPacienteUseCase, Depends(get_paciente_use_case)],
):
    try:
        paciente = await use_case.execute(current_user.id, id)
        return paciente
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {id} no encontrado",
        )


@router.patch("/{id}", response_model=PacienteResponseDTO)
async def update_paciente(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[UpdatePacienteUseCase, Depends(get_update_paciente_use_case)],
    dto: PacienteUpdateDTO,
):
    try:
        paciente = await use_case.execute(current_user.id, id, dto)
        return paciente
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {id} no encontrado",
        )
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paciente(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[DeletePacienteUseCase, Depends(get_delete_paciente_use_case)],
):
    try:
        await use_case.execute(current_user.id, id)
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {id} no encontrado",
        )
