import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock
import pytest

from app.domain.ports.metrica_repository import MetricaRepositoryPort
from app.application.dtos.metrica import (
    PacienteInfoDTO,
    UltimaSesionDTO,
    PacienteResumenMetricasDTO,
    EvolucionItemDTO,
    RendimientoActividadDTO,
    GlobalResumenDTO,
    RankingPacienteItemDTO,
)
from app.application.use_cases.metrica_use_cases import (
    GetPacienteResumenMetricasUseCase,
    GetPacienteEvolucionUseCase,
    GetPacientePorActividadUseCase,
    ExportarSesionesPacienteUseCase,
    GetGlobalResumenUseCase,
    GetRankingPacientesUseCase,
)
from app.infrastructure.db.repositories.sql_metrica_repository import SqlMetricaRepository
from app.infrastructure.db.models.sesion_juego import SesionJuegoModel


class DummySesion:
    def __init__(self, aciertos: int, errores: int, tiempo_segundos: int = 30):
        self.aciertos = aciertos
        self.errores = errores
        self.tiempo_segundos = tiempo_segundos


def test_calcular_tendencia_mejora():
    # Sesiones ordenadas descendentemente:
    # ultimas 3: tasa 1.0 (10/10)
    # anteriores 3: tasa 0.5 (5/10)
    sesiones = [
        DummySesion(10, 0),
        DummySesion(10, 0),
        DummySesion(10, 0),
        DummySesion(5, 5),
        DummySesion(5, 5),
        DummySesion(5, 5),
    ]
    tendencia = SqlMetricaRepository._calcular_tendencia(sesiones)
    assert tendencia == "mejora"


def test_calcular_tendencia_retroceso():
    # ultimas 3: tasa 0.4 (4/10)
    # anteriores 3: tasa 0.9 (9/10)
    sesiones = [
        DummySesion(4, 6),
        DummySesion(4, 6),
        DummySesion(4, 6),
        DummySesion(9, 1),
        DummySesion(9, 1),
        DummySesion(9, 1),
    ]
    tendencia = SqlMetricaRepository._calcular_tendencia(sesiones)
    assert tendencia == "retroceso"


def test_calcular_tendencia_estable():
    # ultimas 3: tasa 0.8 (8/10)
    # anteriores 3: tasa 0.82 (aproximadamente igual, diferencia < 5%)
    sesiones = [
        DummySesion(8, 2),
        DummySesion(8, 2),
        DummySesion(8, 2),
        DummySesion(8, 2),
        DummySesion(8, 2),
        DummySesion(9, 1),
    ]
    tendencia = SqlMetricaRepository._calcular_tendencia(sesiones)
    assert tendencia == "estable"


def test_calcular_tendencia_sin_datos():
    assert SqlMetricaRepository._calcular_tendencia([]) == "sin_datos"


def test_calcular_tendencia_pocas_sesiones():
    assert SqlMetricaRepository._calcular_tendencia([DummySesion(5, 5)]) == "estable"


@pytest.mark.asyncio
async def test_get_paciente_resumen_use_case():
    repo = AsyncMock(spec=MetricaRepositoryPort)
    prof_id = uuid.uuid4()
    pac_id = uuid.uuid4()

    mock_dto = PacienteResumenMetricasDTO(
        paciente=PacienteInfoDTO(id=pac_id, apodo="Luka", edad=6),
        total_sesiones=5,
        tiempo_promedio_seg=42.5,
        tasa_acierto_promedio=0.85,
        ultima_sesion=UltimaSesionDTO(
            fecha=datetime.now(timezone.utc),
            tiempo=40,
            aciertos=8,
            errores=2,
        ),
        tendencia="mejora",
    )
    repo.get_resumen_paciente.return_value = mock_dto

    use_case = GetPacienteResumenMetricasUseCase(repo)
    result = await use_case.execute(prof_id, pac_id)

    assert result.total_sesiones == 5
    assert result.paciente.apodo == "Luka"
    assert result.tendencia == "mejora"
    assert result.tasa_acierto_promedio == 0.85


@pytest.mark.asyncio
async def test_exportar_sesiones_csv_use_case():
    repo = AsyncMock(spec=MetricaRepositoryPort)
    prof_id = uuid.uuid4()
    pac_id = uuid.uuid4()

    repo.get_sesiones_export.return_value = (
        "Luka",
        [
            {
                "sesion_id": str(uuid.uuid4()),
                "fecha": "2026-09-16T12:00:00",
                "actividad": "Animales y Alimentos",
                "tiempo_segundos": 45,
                "aciertos": 8,
                "errores": 1,
                "tasa_acierto": 0.8889,
            }
        ],
    )

    use_case = ExportarSesionesPacienteUseCase(repo)
    apodo, csv_content = await use_case.execute(prof_id, pac_id)

    assert apodo == "Luka"
    assert "sesion_id,fecha,actividad,tiempo_segundos,aciertos,errores,tasa_acierto" in csv_content
    assert "Animales y Alimentos" in csv_content
    assert "0.8889" in csv_content


@pytest.mark.asyncio
async def test_global_resumen_use_case():
    repo = AsyncMock(spec=MetricaRepositoryPort)
    prof_id = uuid.uuid4()

    repo.get_resumen_global.return_value = GlobalResumenDTO(
        total_pacientes=12,
        total_sesiones=45,
        total_actividades=8,
        tasa_acierto_promedio=0.82,
        pacientes_activos_ultimos_7_dias=5,
    )

    use_case = GetGlobalResumenUseCase(repo)
    result = await use_case.execute(prof_id)

    assert result.total_pacientes == 12
    assert result.total_sesiones == 45
    assert result.pacientes_activos_ultimos_7_dias == 5
