import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import {
  getResumenPaciente,
  getEvolucionPaciente,
  getRendimientoPorActividad,
  exportarSesionesCSV,
} from '../services/api';
import {
  PacienteResumenMetricas,
  EvolucionItem,
  RendimientoActividad,
} from '../types';
import {
  ArrowLeft,
  Activity,
  Clock,
  Award,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  Layers,
  FileSpreadsheet,
  RefreshCw,
} from 'lucide-react';

export const PacienteMetricasPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [resumen, setResumen] = useState<PacienteResumenMetricas | null>(null);
  const [evolucion, setEvolucion] = useState<EvolucionItem[]>([]);
  const [porActividad, setPorActividad] = useState<RendimientoActividad[]>([]);
  const [agrupacion, setAgrupacion] = useState<'dia' | 'semana'>('dia');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState<EvolucionItem | null>(null);

  const fetchData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [resumenData, evolucionData, actividadData] = await Promise.all([
        getResumenPaciente(id),
        getEvolucionPaciente(id, { agrupacion }),
        getRendimientoPorActividad(id),
      ]);
      setResumen(resumenData);
      setEvolucion(evolucionData);
      setPorActividad(actividadData);
    } catch (err) {
      console.error('Error al cargar métricas del paciente', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id, agrupacion]);

  const handleExportCSV = async () => {
    if (!id || !resumen) return;
    setExporting(true);
    try {
      await exportarSesionesCSV(id, resumen.paciente.apodo);
    } catch (err) {
      alert('Error al exportar sesiones a CSV');
    } finally {
      setExporting(false);
    }
  };

  const renderTendenciaBadge = (tendencia: string) => {
    switch (tendencia) {
      case 'mejora':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            Tendencia en Mejora (+5%)
          </span>
        );
      case 'retroceso':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-300">
            <TrendingDown className="w-4 h-4 text-red-600" />
            Tendencia en Retroceso (-5%)
          </span>
        );
      case 'estable':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-300">
            <Minus className="w-4 h-4 text-blue-600" />
            Tendencia Estable
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
            Sin sesiones suficientes
          </span>
        );
    }
  };

  // Dimensiones para el SVG interactivo
  const svgWidth = 700;
  const svgHeight = 260;
  const padding = { top: 30, right: 30, bottom: 40, left: 50 };

  const graphWidth = svgWidth - padding.left - padding.right;
  const graphHeight = svgHeight - padding.top - padding.bottom;

  // Cálculo de puntos de la curva de aprendizaje (Tasa de acierto: 0 a 1)
  const points = evolucion.map((item, index) => {
    const x =
      evolucion.length === 1
        ? padding.left + graphWidth / 2
        : padding.left + (index / (evolucion.length - 1)) * graphWidth;
    const y = padding.top + (1 - item.tasa_acierto) * graphHeight;
    return { x, y, item };
  });

  const pathD =
    points.length > 0
      ? points.reduce(
          (acc, p, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`,
          ''
        )
      : '';

  const areaD =
    points.length > 0
      ? `${pathD} L ${points[points.length - 1].x} ${padding.top + graphHeight} L ${
          points[0].x
        } ${padding.top + graphHeight} Z`
      : '';

  return (
    <Layout>
      <div className="space-y-8 max-w-7xl mx-auto pb-12">
        {/* Header de Navegación y Exportación */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/pacientes')}
              className="p-2.5 rounded-xl border border-slate-200 bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition shadow-sm"
              title="Volver a pacientes"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-extrabold text-slate-800">
                  {loading ? 'Cargando paciente...' : resumen?.paciente.apodo}
                </h1>
                {resumen && renderTendenciaBadge(resumen.tendencia)}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {resumen?.paciente.edad ? `${resumen.paciente.edad} años` : 'Edad no indicada'} • Identificador UUID: {id}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              className="p-2.5 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition shadow-sm"
              title="Recargar métricas"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={handleExportCSV}
              disabled={exporting || !resumen || resumen.total_sesiones === 0}
              className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl font-bold text-sm shadow-md transition cursor-pointer"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>{exporting ? 'Generando...' : 'Exportar CSV'}</span>
            </button>
          </div>
        </div>

        {/* Tarjetas KPI de Rendimiento Individual */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Sesiones */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600">
              <Activity className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Sesiones</p>
              <h3 className="text-2xl font-extrabold text-slate-800 mt-0.5">
                {loading ? '...' : resumen?.total_sesiones ?? 0}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Actividades completadas</p>
            </div>
          </div>

          {/* Tasa Acierto Promedio */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600">
              <Award className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tasa de Acierto</p>
              <h3 className="text-2xl font-extrabold text-emerald-600 mt-0.5">
                {loading ? '...' : `${Math.round((resumen?.tasa_acierto_promedio ?? 0) * 100)}%`}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Aciertos vs Errores</p>
            </div>
          </div>

          {/* Tiempo Promedio */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600">
              <Clock className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tiempo Promedio</p>
              <h3 className="text-2xl font-extrabold text-slate-800 mt-0.5">
                {loading ? '...' : `${resumen?.tiempo_promedio_seg ?? 0}s`}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Por sesión jugada</p>
            </div>
          </div>

          {/* Resumen Última Sesión */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-purple-50 flex items-center justify-center text-purple-600">
              <Calendar className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Última Sesión</p>
              {resumen?.ultima_sesion ? (
                <div>
                  <h3 className="text-sm font-extrabold text-slate-800 mt-0.5">
                    {new Date(resumen.ultima_sesion.fecha || '').toLocaleDateString('es-ES', {
                      day: '2-digit',
                      month: 'short',
                    })}{' '}
                    • {resumen.ultima_sesion.tiempo}s
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {resumen.ultima_sesion.aciertos} aciertos / {resumen.ultima_sesion.errores} fallos
                  </p>
                </div>
              ) : (
                <p className="text-xs text-slate-400 mt-1">Sin registros aún</p>
              )}
            </div>
          </div>
        </div>

        {/* Gráfico de Evolución Temporal (Curva de Aprendizaje) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                Curva de Aprendizaje y Evolución Temporal
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Representación de la tasa de acierto y regularidad de las sesiones.
              </p>
            </div>

            {/* Selector Día / Semana */}
            <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
              <button
                onClick={() => setAgrupacion('dia')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  agrupacion === 'dia'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Por Día
              </button>
              <button
                onClick={() => setAgrupacion('semana')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                  agrupacion === 'semana'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Por Semana
              </button>
            </div>
          </div>

          {/* Renderizado de SVG */}
          {evolucion.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 space-y-2">
              <Activity className="w-8 h-8 text-slate-300" />
              <p className="text-sm font-medium">No hay suficientes sesiones para trazar la curva temporal.</p>
              <p className="text-xs text-slate-400">Genera un enlace de actividad y completa sesiones con el paciente.</p>
            </div>
          ) : (
            <div className="relative overflow-x-auto">
              {hoveredPoint && (
                <div
                  className="absolute z-20 bg-slate-900 text-white text-xs rounded-xl p-3 shadow-xl pointer-events-none transition-all duration-150"
                  style={{
                    left: `${hoveredPoint ? points.find((p) => p.item.fecha === hoveredPoint.fecha)?.x || 100 : 0}px`,
                    top: '10px',
                    transform: 'translateX(-50%)',
                  }}
                >
                  <p className="font-bold border-b border-slate-700 pb-1 mb-1">{hoveredPoint.fecha}</p>
                  <p className="text-emerald-400">
                    Aciertos: {Math.round(hoveredPoint.tasa_acierto * 100)}%
                  </p>
                  <p className="text-slate-300">Sesiones: {hoveredPoint.sesiones}</p>
                  <p className="text-slate-300">Tiempo medio: {hoveredPoint.tiempo_promedio}s</p>
                </div>
              )}

              <svg
                viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                className="w-full h-64 select-none overflow-visible"
              >
                <defs>
                  <linearGradient id="gradientEvolution" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Líneas de Guía Horizontales */}
                {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
                  const y = padding.top + (1 - ratio) * graphHeight;
                  return (
                    <g key={ratio}>
                      <line
                        x1={padding.left}
                        y1={y}
                        x2={padding.left + graphWidth}
                        y2={y}
                        stroke="#E2E8F0"
                        strokeDasharray={ratio === 0 || ratio === 1 ? 'none' : '4 4'}
                        strokeWidth="1"
                      />
                      <text
                        x={padding.left - 10}
                        y={y + 4}
                        textAnchor="end"
                        className="text-[10px] fill-slate-400 font-mono font-medium"
                      >
                        {Math.round(ratio * 100)}%
                      </text>
                    </g>
                  );
                })}

                {/* Área bajo la curva */}
                {points.length > 1 && (
                  <path d={areaD} fill="url(#gradientEvolution)" />
                )}

                {/* Línea de la Curva */}
                {points.length > 1 && (
                  <path
                    d={pathD}
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}

                {/* Puntos y Etiquetas de Fecha */}
                {points.map((p, idx) => (
                  <g key={idx}>
                    <circle
                      cx={p.x}
                      cy={p.y}
                      r={hoveredPoint?.fecha === p.item.fecha ? 7 : 5}
                      className="fill-blue-600 stroke-white stroke-2 cursor-pointer transition-all duration-150 hover:fill-blue-800"
                      onMouseEnter={() => setHoveredPoint(p.item)}
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                    <text
                      x={p.x}
                      y={padding.top + graphHeight + 20}
                      textAnchor="middle"
                      className="text-[10px] fill-slate-500 font-medium"
                    >
                      {p.item.fecha.slice(5)}
                    </text>
                  </g>
                ))}
              </svg>
            </div>
          )}
        </div>

        {/* Desglose de Rendimiento por Actividad */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-600" />
                Rendimiento Desglosado por Actividad
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Eficacia del paciente en cada plantilla y ejercicio asignado.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50/75 text-xs uppercase font-bold text-slate-400 border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Actividad Terapéutica</th>
                  <th className="px-6 py-4">Sesiones Completadas</th>
                  <th className="px-6 py-4">Tiempo Promedio</th>
                  <th className="px-6 py-4">Tasa de Acierto</th>
                  <th className="px-6 py-4 text-right">Eficacia</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {porActividad.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-slate-400">
                      No hay registros de actividades jugadas para este paciente.
                    </td>
                  </tr>
                ) : (
                  porActividad.map((act, i) => {
                    const porcentaje = Math.round(act.tasa_acierto * 100);
                    return (
                      <tr key={i} className="hover:bg-slate-50/70 transition">
                        <td className="px-6 py-4 font-bold text-slate-800">
                          {act.titulo}
                        </td>
                        <td className="px-6 py-4 text-slate-700 font-semibold">
                          {act.sesiones}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {act.tiempo_promedio} seg
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="font-bold text-slate-800 text-sm w-10">
                              {porcentaje}%
                            </span>
                            <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  porcentaje >= 75
                                    ? 'bg-emerald-500'
                                    : porcentaje >= 50
                                    ? 'bg-blue-500'
                                    : 'bg-amber-500'
                                }`}
                                style={{ width: `${porcentaje}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span
                            className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold ${
                              porcentaje >= 80
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : porcentaje >= 50
                                ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            {porcentaje >= 80 ? 'Dominada' : porcentaje >= 50 ? 'En progreso' : 'Requiere apoyo'}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};
