from typing import Annotated, List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.domain.models.profesional import Profesional
from app.domain.exceptions import PacienteNotFoundException, DomainException
from app.application.dtos.metrica import (
    PacienteResumenMetricasDTO,
    EvolucionItemDTO,
    RendimientoActividadDTO,
    GlobalResumenDTO,
    RankingPacienteItemDTO,
)
from app.application.use_cases import (
    GetPacienteResumenMetricasUseCase,
    GetPacienteEvolucionUseCase,
    GetPacientePorActividadUseCase,
    ExportarSesionesPacienteUseCase,
    GetGlobalResumenUseCase,
    GetRankingPacientesUseCase,
)
from app.presentation.api.v1.dependencies import (
    get_current_user,
    get_paciente_resumen_metricas_use_case,
    get_paciente_evolucion_use_case,
    get_paciente_por_actividad_use_case,
    get_exportar_sesiones_paciente_use_case,
    get_global_resumen_use_case,
    get_ranking_pacientes_use_case,
)

router = APIRouter(prefix="/metricas", tags=["Métricas y Evaluación"])


# -------------------------------------------------------------------------
# Métricas por paciente
# -------------------------------------------------------------------------

@router.get("/paciente/{paciente_id}/resumen", response_model=PacienteResumenMetricasDTO)
async def get_resumen_paciente(
    paciente_id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetPacienteResumenMetricasUseCase, Depends(get_paciente_resumen_metricas_use_case)],
):
    """Devuelve el resumen de métricas del paciente (KPIs, última sesión y tendencia)."""
    try:
        return await use_case.execute(current_user.id, paciente_id)
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/paciente/{paciente_id}/evolucion", response_model=List[EvolucionItemDTO])
async def get_evolucion_paciente(
    paciente_id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetPacienteEvolucionUseCase, Depends(get_paciente_evolucion_use_case)],
    desde: Optional[date] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    agrupacion: str = Query("dia", description="Agrupación temporal: dia | semana"),
):
    """Devuelve la serie temporal de evolución agrupada por día o por semana."""
    try:
        return await use_case.execute(
            profesional_id=current_user.id,
            paciente_id=paciente_id,
            desde=desde,
            hasta=hasta,
            agrupacion=agrupacion,
        )
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/paciente/{paciente_id}/por-actividad", response_model=List[RendimientoActividadDTO])
async def get_rendimiento_por_actividad(
    paciente_id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetPacientePorActividadUseCase, Depends(get_paciente_por_actividad_use_case)],
):
    """Devuelve el desglose de rendimiento del paciente agrupado por actividad."""
    try:
        return await use_case.execute(current_user.id, paciente_id)
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/paciente/{paciente_id}/export")
async def exportar_metricas_paciente(
    paciente_id: UUID,
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[ExportarSesionesPacienteUseCase, Depends(get_exportar_sesiones_paciente_use_case)],
    formato: str = Query("csv", description="Formato de exportación: csv | pdf"),
):
    """
    Exportación de sesiones del paciente.
    - csv: Descarga archivo CSV adjunto.
    - pdf: Endpoint preparado para Fase 2 (retorna 501 Not Implemented).
    """
    formato_lower = formato.lower()
    if formato_lower == "pdf":
        # TODO: Fase 2 - Implementar generación de informe clínico en PDF con ReportLab/WeasyPrint
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La exportación a formato PDF está prevista para la Fase 2.",
        )
    elif formato_lower != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato '{formato}' no soportado. Formatos válidos: csv, pdf",
        )

    try:
        apodo, csv_content = await use_case.execute(current_user.id, paciente_id)
        filename = f"paciente_{apodo.replace(' ', '_')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except PacienteNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {paciente_id} no encontrado",
        )
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------------------------------------------------------
# Métricas globales del profesional
# -------------------------------------------------------------------------

@router.get("/global/resumen", response_model=GlobalResumenDTO)
async def get_resumen_global(
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetGlobalResumenUseCase, Depends(get_global_resumen_use_case)],
):
    """Devuelve las métricas globales consolidadas del profesional."""
    try:
        return await use_case.execute(current_user.id)
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/global/ranking-pacientes", response_model=List[RankingPacienteItemDTO])
async def get_ranking_pacientes(
    current_user: Annotated[Profesional, Depends(get_current_user)],
    use_case: Annotated[GetRankingPacientesUseCase, Depends(get_ranking_pacientes_use_case)],
    orden: str = Query("progreso", description="Criterio de ordenación: progreso | actividad"),
):
    """Devuelve el listado ordenado de pacientes con sus tasas de acierto y tendencia."""
    try:
        return await use_case.execute(current_user.id, orden=orden)
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
