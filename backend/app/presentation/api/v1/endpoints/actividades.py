import os
import shutil
from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status

from app.domain.models.profesional import Profesional
from app.domain.exceptions import (
    ActividadNotFoundException,
    ActividadInvalidaException,
    DomainException,
)
from app.application.dtos.actividad import (
    ActividadCreateDTO,
    ActividadUpdateDTO,
    ActividadResponseDTO,
    ActividadListResponseDTO,
    EnlaceResponseDTO,
)
from app.application.use_cases import (
    CreateActividadUseCase,
    ListActividadesUseCase,
    GetActividadUseCase,
    UpdateActividadUseCase,
    DeleteActividadUseCase,
    GenerarEnlaceUseCase,
)
from app.presentation.api.v1.dependencies import (
    get_current_user,
    get_create_actividad_use_case,
    get_list_actividades_use_case,
    get_actividad_use_case,
    get_update_actividad_use_case,
    get_delete_actividad_use_case,
    get_generar_enlace_use_case,
)

router = APIRouter(prefix="/actividades", tags=["Actividades"])


@router.post("", response_model=ActividadResponseDTO, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ActividadResponseDTO, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_actividad(
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[CreateActividadUseCase, Depends(get_create_actividad_use_case)],
    dto: ActividadCreateDTO,
):
    try:
        actividad = await use_case.execute(current_user.id, dto)
        return actividad
    except (ActividadInvalidaException, DomainException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ActividadListResponseDTO)
@router.get("/", response_model=ActividadListResponseDTO, include_in_schema=False)
async def list_actividades(

    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[ListActividadesUseCase, Depends(get_list_actividades_use_case)],
    paciente_id: Optional[UUID] = Query(None, description="Filtrar por ID de paciente"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de plantilla"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
):
    items, total = await use_case.execute(
        profesional_id=current_user.id,
        paciente_id=paciente_id,
        tipo_plantilla=tipo,
        page=page,
        size=size,
    )
    return ActividadListResponseDTO(
        items=[ActividadResponseDTO.model_validate(a) for a in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{id}", response_model=ActividadResponseDTO)
async def get_actividad(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetActividadUseCase, Depends(get_actividad_use_case)],
):
    try:
        actividad = await use_case.execute(current_user.id, id)
        return actividad
    except ActividadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad con ID {id} no encontrada",
        )


@router.patch("/{id}", response_model=ActividadResponseDTO)
async def update_actividad(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[UpdateActividadUseCase, Depends(get_update_actividad_use_case)],
    dto: ActividadUpdateDTO,
):
    try:
        actividad = await use_case.execute(current_user.id, id, dto)
        return actividad
    except ActividadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad con ID {id} no encontrada",
        )
    except (ActividadInvalidaException, DomainException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actividad(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[DeleteActividadUseCase, Depends(get_delete_actividad_use_case)],
):
    try:
        await use_case.execute(current_user.id, id)
    except ActividadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad con ID {id} no encontrada",
        )


@router.post("/{id}/enlace", response_model=EnlaceResponseDTO, tags=["Enlaces"])
async def generar_enlace(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GenerarEnlaceUseCase, Depends(get_generar_enlace_use_case)],
):
    try:
        token, expira_en = await use_case.execute(current_user.id, id)
        return EnlaceResponseDTO(
            token=token,
            url_completa=f"/play/{token}",
            expira_en=expira_en,
        )
    except ActividadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad con ID {id} no encontrada",
        )


@router.post("/{id}/assets")
async def subir_assets(
    id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    get_use_case: Annotated[GetActividadUseCase, Depends(get_actividad_use_case)],
    files: List[UploadFile] = File(...),
):
    try:
        await get_use_case.execute(current_user.id, id)
    except ActividadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad con ID {id} no encontrada",
        )

    storage_dir = os.path.join("storage", str(current_user.id), str(id))
    os.makedirs(storage_dir, exist_ok=True)

    uploaded_urls = []
    for file in files:
        if not file.filename:
            continue
        safe_filename = os.path.basename(file.filename)
        dest_path = os.path.join(storage_dir, safe_filename)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_urls.append(f"/static/{current_user.id}/{id}/{safe_filename}")

    return {"uploaded_files": uploaded_urls}
