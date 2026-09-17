from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select, func, case, desc, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ports.metrica_repository import MetricaRepositoryPort
from app.domain.exceptions import PacienteNotFoundException
from app.infrastructure.db.models.paciente import PacienteModel
from app.infrastructure.db.models.actividad import ActividadModel
from app.infrastructure.db.models.sesion_juego import SesionJuegoModel
from app.application.dtos.metrica import (
    PacienteInfoDTO,
    UltimaSesionDTO,
    PacienteResumenMetricasDTO,
    EvolucionItemDTO,
    RendimientoActividadDTO,
    GlobalResumenDTO,
    RankingPacienteItemDTO,
)


class SqlMetricaRepository(MetricaRepositoryPort):
    """Implementación SQLAlchemy de MetricaRepositoryPort."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _verificar_paciente_profesional(self, profesional_id: UUID, paciente_id: UUID) -> PacienteModel:
        stmt = select(PacienteModel).where(
            PacienteModel.id == paciente_id,
            PacienteModel.profesional_id == profesional_id,
            PacienteModel.eliminado_en.is_(None),
        )
        res = await self.session.execute(stmt)
        paciente = res.scalar_one_or_none()
        if not paciente:
            raise PacienteNotFoundException(str(paciente_id))
        return paciente

    @staticmethod
    def _calcular_tendencia(sesiones: List[SesionJuegoModel]) -> str:
        """
        Calcula la tendencia comparando la tasa de acierto promedio
        de las últimas 3 sesiones vs las 3 sesiones anteriores.
        - Mejora > 5% (+0.05) -> 'mejora'
        - Empeora > 5% (-0.05) -> 'retroceso'
        - En otro caso -> 'estable'
        - Si hay menos de 2 sesiones -> 'estable' (o 'sin_datos' si 0)
        """
        if not sesiones:
            return "sin_datos"
        if len(sesiones) < 2:
            return "estable"

        # sesiones vienen ordenadas descendentemente por completado_en o id
        ultimas = sesiones[:3]
        anteriores = sesiones[3:6]

        if not anteriores:
            # Si sólo hay entre 2 y 3 sesiones, comparamos la más reciente con las anteriores
            ultimas = sesiones[:1]
            anteriores = sesiones[1:]

        def calc_tasa(ses_list):
            total_ac = sum(s.aciertos for s in ses_list)
            total_err = sum(s.errores for s in ses_list)
            total = total_ac + total_err
            return (total_ac / total) if total > 0 else 0.0

        tasa_ultimas = calc_tasa(ultimas)
        tasa_anteriores = calc_tasa(anteriores)

        diferencia = tasa_ultimas - tasa_anteriores
        if diferencia > 0.05:
            return "mejora"
        elif diferencia < -0.05:
            return "retroceso"
        return "estable"

    async def get_resumen_paciente(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> Optional[PacienteResumenMetricasDTO]:
        paciente = await self._verificar_paciente_profesional(profesional_id, paciente_id)

        # Buscar todas las sesiones para cálculos agregados y tendencia
        stmt_sesiones = (
            select(SesionJuegoModel)
            .where(SesionJuegoModel.paciente_id == paciente_id)
            .order_by(SesionJuegoModel.completado_en.desc())
        )
        res_sesiones = await self.session.execute(stmt_sesiones)
        sesiones = list(res_sesiones.scalars().all())

        total_sesiones = len(sesiones)
        if total_sesiones == 0:
            return PacienteResumenMetricasDTO(
                paciente=PacienteInfoDTO(id=paciente.id, apodo=paciente.apodo, edad=paciente.edad),
                total_sesiones=0,
                tiempo_promedio_seg=0.0,
                tasa_acierto_promedio=0.0,
                ultima_sesion=None,
                tendencia="sin_datos",
            )

        tiempo_total = sum(s.tiempo_segundos for s in sesiones)
        tiempo_promedio_seg = round(tiempo_total / total_sesiones, 2)

        total_aciertos = sum(s.aciertos for s in sesiones)
        total_errores = sum(s.errores for s in sesiones)
        total_intentos = total_aciertos + total_errores
        tasa_acierto_promedio = round((total_aciertos / total_intentos), 4) if total_intentos > 0 else 0.0

        ultima_s = sesiones[0]
        ultima_dto = UltimaSesionDTO(
            fecha=ultima_s.completado_en,
            tiempo=ultima_s.tiempo_segundos,
            aciertos=ultima_s.aciertos,
            errores=ultima_s.errores,
        )

        tendencia = self._calcular_tendencia(sesiones)

        return PacienteResumenMetricasDTO(
            paciente=PacienteInfoDTO(id=paciente.id, apodo=paciente.apodo, edad=paciente.edad),
            total_sesiones=total_sesiones,
            tiempo_promedio_seg=tiempo_promedio_seg,
            tasa_acierto_promedio=tasa_acierto_promedio,
            ultima_sesion=ultima_dto,
            tendencia=tendencia,
        )

    async def get_evolucion_paciente(
        self,
        profesional_id: UUID,
        paciente_id: UUID,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        agrupacion: str = "dia",
    ) -> List[EvolucionItemDTO]:
        await self._verificar_paciente_profesional(profesional_id, paciente_id)

        # Determinar función de agrupación de fecha
        if agrupacion == "semana":
            date_col = func.date_trunc("week", SesionJuegoModel.completado_en).label("fecha_grupo")
        else:
            date_col = func.date(SesionJuegoModel.completado_en).label("fecha_grupo")

        conditions = [SesionJuegoModel.paciente_id == paciente_id]
        if desde:
            conditions.append(func.date(SesionJuegoModel.completado_en) >= desde)
        if hasta:
            conditions.append(func.date(SesionJuegoModel.completado_en) <= hasta)

        stmt = (
            select(
                date_col,
                func.count(SesionJuegoModel.id).label("sesiones"),
                func.avg(SesionJuegoModel.tiempo_segundos).label("tiempo_promedio"),
                func.sum(SesionJuegoModel.aciertos).label("sum_aciertos"),
                func.sum(SesionJuegoModel.errores).label("sum_errores"),
            )
            .where(and_(*conditions))
            .group_by(date_col)
            .order_by(date_col.asc())
        )

        res = await self.session.execute(stmt)
        rows = res.all()

        evolucion: List[EvolucionItemDTO] = []
        for row in rows:
            fecha_val = row.fecha_grupo
            if isinstance(fecha_val, datetime):
                fecha_str = fecha_val.strftime("%Y-%m-%d")
            elif isinstance(fecha_val, date):
                fecha_str = fecha_val.isoformat()
            else:
                fecha_str = str(fecha_val)

            sum_aciertos = row.sum_aciertos or 0
            sum_errores = row.sum_errores or 0
            total_intentos = sum_aciertos + sum_errores
            tasa = round(sum_aciertos / total_intentos, 4) if total_intentos > 0 else 0.0

            evolucion.append(
                EvolucionItemDTO(
                    fecha=fecha_str,
                    sesiones=int(row.sesiones or 0),
                    tiempo_promedio=round(float(row.tiempo_promedio or 0.0), 2),
                    tasa_acierto=tasa,
                )
            )

        return evolucion

    async def get_rendimiento_por_actividad(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> List[RendimientoActividadDTO]:
        await self._verificar_paciente_profesional(profesional_id, paciente_id)

        stmt = (
            select(
                SesionJuegoModel.actividad_id,
                func.coalesce(ActividadModel.titulo, "Actividad no asignada").label("titulo"),
                func.count(SesionJuegoModel.id).label("sesiones"),
                func.avg(SesionJuegoModel.tiempo_segundos).label("tiempo_promedio"),
                func.sum(SesionJuegoModel.aciertos).label("sum_aciertos"),
                func.sum(SesionJuegoModel.errores).label("sum_errores"),
            )
            .outerjoin(ActividadModel, SesionJuegoModel.actividad_id == ActividadModel.id)
            .where(SesionJuegoModel.paciente_id == paciente_id)
            .group_by(SesionJuegoModel.actividad_id, ActividadModel.titulo)
            .order_by(desc("sesiones"))
        )

        res = await self.session.execute(stmt)
        rows = res.all()

        items: List[RendimientoActividadDTO] = []
        for row in rows:
            sum_aciertos = row.sum_aciertos or 0
            sum_errores = row.sum_errores or 0
            total_intentos = sum_aciertos + sum_errores
            tasa = round(sum_aciertos / total_intentos, 4) if total_intentos > 0 else 0.0

            items.append(
                RendimientoActividadDTO(
                    actividad_id=row.actividad_id,
                    titulo=row.titulo,
                    sesiones=int(row.sesiones or 0),
                    tiempo_promedio=round(float(row.tiempo_promedio or 0.0), 2),
                    tasa_acierto=tasa,
                )
            )

        return items

    async def get_sesiones_export(
        self, profesional_id: UUID, paciente_id: UUID
    ) -> Tuple[str, List[Dict[str, Any]]]:
        paciente = await self._verificar_paciente_profesional(profesional_id, paciente_id)

        stmt = (
            select(
                SesionJuegoModel.id,
                SesionJuegoModel.completado_en,
                SesionJuegoModel.tiempo_segundos,
                SesionJuegoModel.aciertos,
                SesionJuegoModel.errores,
                func.coalesce(ActividadModel.titulo, "Actividad General").label("actividad_titulo"),
            )
            .outerjoin(ActividadModel, SesionJuegoModel.actividad_id == ActividadModel.id)
            .where(SesionJuegoModel.paciente_id == paciente_id)
            .order_by(SesionJuegoModel.completado_en.desc())
        )

        res = await self.session.execute(stmt)
        rows = res.all()

        data: List[Dict[str, Any]] = []
        for r in rows:
            total = (r.aciertos or 0) + (r.errores or 0)
            tasa = round((r.aciertos or 0) / total, 4) if total > 0 else 0.0
            data.append({
                "sesion_id": str(r.id),
                "fecha": r.completado_en.isoformat() if r.completado_en else "",
                "actividad": r.actividad_titulo,
                "tiempo_segundos": r.tiempo_segundos,
                "aciertos": r.aciertos,
                "errores": r.errores,
                "tasa_acierto": tasa,
            })

        return paciente.apodo, data

    async def get_resumen_global(self, profesional_id: UUID) -> GlobalResumenDTO:
        # Total pacientes del profesional
        stmt_pacientes = select(func.count(PacienteModel.id)).where(
            PacienteModel.profesional_id == profesional_id,
            PacienteModel.eliminado_en.is_(None),
        )
        total_pacientes = (await self.session.execute(stmt_pacientes)).scalar() or 0

        # Total actividades del profesional
        stmt_actividades = select(func.count(ActividadModel.id)).where(
            ActividadModel.profesional_id == profesional_id,
            ActividadModel.eliminado_en.is_(None),
        )
        total_actividades = (await self.session.execute(stmt_actividades)).scalar() or 0

        # Subquery de pacientes del profesional
        subq_pacientes = (
            select(PacienteModel.id)
            .where(
                PacienteModel.profesional_id == profesional_id,
                PacienteModel.eliminado_en.is_(None),
            )
            .scalar_subquery()
        )

        # Métricas de sesiones asociadas a los pacientes del profesional
        stmt_sesiones = (
            select(
                func.count(SesionJuegoModel.id).label("total_sesiones"),
                func.sum(SesionJuegoModel.aciertos).label("sum_aciertos"),
                func.sum(SesionJuegoModel.errores).label("sum_errores"),
            )
            .where(SesionJuegoModel.paciente_id.in_(subq_pacientes))
        )
        res_sesiones = (await self.session.execute(stmt_sesiones)).one_or_none()

        total_sesiones = res_sesiones.total_sesiones or 0 if res_sesiones else 0
        sum_ac = res_sesiones.sum_aciertos or 0 if res_sesiones else 0
        sum_err = res_sesiones.sum_errores or 0 if res_sesiones else 0
        total_intentos = sum_ac + sum_err
        tasa_global = round(sum_ac / total_intentos, 4) if total_intentos > 0 else 0.0

        # Pacientes activos últimos 7 días
        hace_7_dias = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        stmt_activos = (
            select(func.count(func.distinct(SesionJuegoModel.paciente_id)))
            .where(
                SesionJuegoModel.paciente_id.in_(subq_pacientes),
                SesionJuegoModel.completado_en >= hace_7_dias,
            )
        )
        activos_7_dias = (await self.session.execute(stmt_activos)).scalar() or 0

        return GlobalResumenDTO(
            total_pacientes=total_pacientes,
            total_sesiones=total_sesiones,
            total_actividades=total_actividades,
            tasa_acierto_promedio=tasa_global,
            pacientes_activos_ultimos_7_dias=activos_7_dias,
        )

    async def get_ranking_pacientes(
        self, profesional_id: UUID, orden: str = "progreso"
    ) -> List[RankingPacienteItemDTO]:
        # Obtener todos los pacientes del profesional
        stmt_p = select(PacienteModel).where(
            PacienteModel.profesional_id == profesional_id,
            PacienteModel.eliminado_en.is_(None),
        )
        pacientes = list((await self.session.execute(stmt_p)).scalars().all())

        items: List[RankingPacienteItemDTO] = []
        for p in pacientes:
            stmt_s = (
                select(SesionJuegoModel)
                .where(SesionJuegoModel.paciente_id == p.id)
                .order_by(SesionJuegoModel.completado_en.desc())
            )
            sesiones = list((await self.session.execute(stmt_s)).scalars().all())
            total_s = len(sesiones)
            if total_s > 0:
                sum_ac = sum(s.aciertos for s in sesiones)
                sum_err = sum(s.errores for s in sesiones)
                tot = sum_ac + sum_err
                tasa = round(sum_ac / tot, 4) if tot > 0 else 0.0
                tendencia = self._calcular_tendencia(sesiones)
                ultima_fecha = sesiones[0].completado_en
            else:
                tasa = 0.0
                tendencia = "sin_datos"
                ultima_fecha = None

            items.append(
                RankingPacienteItemDTO(
                    paciente_id=p.id,
                    apodo=p.apodo,
                    edad=p.edad,
                    total_sesiones=total_s,
                    tasa_acierto_promedio=tasa,
                    tendencia=tendencia,
                    ultima_sesion=ultima_fecha,
                )
            )

        if orden == "actividad":
            # Ordenar por mayor número de sesiones
            items.sort(key=lambda x: x.total_sesiones, reverse=True)
        else:
            # Ordenar por progreso (tasa de acierto promedio desc)
            items.sort(key=lambda x: x.tasa_acierto_promedio, reverse=True)

        return items
