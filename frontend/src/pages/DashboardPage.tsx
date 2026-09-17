import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { getGlobalResumen, getRankingPacientes } from '../services/api';
import { GlobalResumen, RankingPacienteItem } from '../types';
import {
  Users,
  Activity,
  Award,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  ChevronRight,
  Filter,
  BarChart3,
  Calendar,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [resumen, setResumen] = useState<GlobalResumen | null>(null);
  const [ranking, setRanking] = useState<RankingPacienteItem[]>([]);
  const [orden, setOrden] = useState<'progreso' | 'actividad'>('progreso');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [resumenData, rankingData] = await Promise.all([
          getGlobalResumen(),
          getRankingPacientes(orden),
        ]);
        setResumen(resumenData);
        setRanking(rankingData);
      } catch (err) {
        console.error('Error al cargar datos del dashboard', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [orden]);

  const renderTendenciaBadge = (tendencia: string) => {
    switch (tendencia) {
      case 'mejora':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <TrendingUp className="w-3.5 h-3.5" />
            Mejora (+5%)
          </span>
        );
      case 'retroceso':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
            <TrendingDown className="w-3.5 h-3.5" />
            Retroceso (-5%)
          </span>
        );
      case 'estable':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Minus className="w-3.5 h-3.5" />
            Estable
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            Sin datos
          </span>
        );
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Banner de Bienvenida y Métricas */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-8 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Dashboard de Evaluación y Rendimiento</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Métricas Globales de Pacientes
            </h1>
            <p className="mt-2 text-blue-100 max-w-xl text-sm leading-relaxed">
              Monitorea el progreso terapéutico, curvas de aprendizaje y participación activa de tus pacientes de forma consolidada.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/pacientes')}
              className="px-5 py-2.5 bg-white text-blue-700 rounded-2xl font-bold text-sm shadow-md hover:bg-blue-50 transition cursor-pointer"
            >
              Gestionar Pacientes
            </button>
            <button
              onClick={() => navigate('/actividades')}
              className="px-5 py-2.5 bg-blue-800/60 border border-white/20 text-white rounded-2xl font-bold text-sm hover:bg-blue-800 transition cursor-pointer"
            >
              Ver Actividades
            </button>
          </div>
        </div>

        {/* Tarjetas KPI Globales */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600">
              <Users className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Pacientes</p>
              <h3 className="text-2xl font-extrabold text-slate-800 mt-0.5">
                {loading ? '...' : resumen?.total_pacientes ?? 0}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Registrados activos</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600">
              <Activity className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sesiones Jugadas</p>
              <h3 className="text-2xl font-extrabold text-slate-800 mt-0.5">
                {loading ? '...' : resumen?.total_sesiones ?? 0}
              </h3>
              <p className="text-xs text-slate-500 mt-1">En el motor de juego</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600">
              <Award className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tasa Acierto Global</p>
              <h3 className="text-2xl font-extrabold text-emerald-600 mt-0.5">
                {loading ? '...' : `${Math.round((resumen?.tasa_acierto_promedio ?? 0) * 100)}%`}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Promedio de éxito</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-13 h-13 rounded-2xl bg-purple-50 flex items-center justify-center text-purple-600">
              <Calendar className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Activos Últimos 7 Días</p>
              <h3 className="text-2xl font-extrabold text-purple-600 mt-0.5">
                {loading ? '...' : resumen?.pacientes_activos_ultimos_7_dias ?? 0}
              </h3>
              <p className="text-xs text-slate-500 mt-1">Pacientes con sesiones</p>
            </div>
          </div>
        </div>

        {/* Ranking y Monitoreo de Pacientes */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Monitoreo y Rendimiento de Pacientes
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Selecciona un paciente para acceder a su curva de aprendizaje detallada y reportes de sesión.
              </p>
            </div>

            {/* Selector de Orden */}
            <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
              <Filter className="w-4 h-4 text-slate-400 ml-1" />
              <button
                onClick={() => setOrden('progreso')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  orden === 'progreso'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Por Progreso (Tasa Acierto)
              </button>
              <button
                onClick={() => setOrden('actividad')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  orden === 'actividad'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Por Actividad (Sesiones)
              </button>
            </div>
          </div>

          {/* Tabla de Ranking */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50/75 text-xs uppercase font-bold text-slate-400 border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4">Paciente</th>
                  <th className="px-6 py-4">Edad</th>
                  <th className="px-6 py-4">Sesiones</th>
                  <th className="px-6 py-4">Tasa de Acierto</th>
                  <th className="px-6 py-4">Tendencia</th>
                  <th className="px-6 py-4">Última Sesión</th>
                  <th className="px-6 py-4 text-right">Acción</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                      Cargando datos de rendimiento...
                    </td>
                  </tr>
                ) : ranking.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                      No hay pacientes registrados aún. Crea tu primer paciente para ver sus métricas.
                    </td>
                  </tr>
                ) : (
                  ranking.map((p) => {
                    const porcentajeAcierto = Math.round(p.tasa_acierto_promedio * 100);

                    return (
                      <tr
                        key={p.paciente_id}
                        className="hover:bg-slate-50/80 transition cursor-pointer group"
                        onClick={() => navigate(`/pacientes/${p.paciente_id}/metricas`)}
                      >
                        <td className="px-6 py-4 font-bold text-slate-800 flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm group-hover:bg-blue-600 group-hover:text-white transition">
                            {p.apodo.charAt(0).toUpperCase()}
                          </div>
                          <span>{p.apodo}</span>
                        </td>
                        <td className="px-6 py-4">
                          {p.edad ? `${p.edad} años` : 'Sin especificar'}
                        </td>
                        <td className="px-6 py-4 font-semibold text-slate-700">
                          {p.total_sesiones}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="font-bold text-slate-800 text-sm w-10">
                              {porcentajeAcierto}%
                            </span>
                            <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  porcentajeAcierto >= 75
                                    ? 'bg-emerald-500'
                                    : porcentajeAcierto >= 50
                                    ? 'bg-blue-500'
                                    : 'bg-amber-500'
                                }`}
                                style={{ width: `${porcentajeAcierto}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {renderTendenciaBadge(p.tendencia)}
                        </td>
                        <td className="px-6 py-4 text-slate-500 text-xs">
                          {p.ultima_sesion
                            ? new Date(p.ultima_sesion).toLocaleDateString('es-ES', {
                                day: '2-digit',
                                month: 'short',
                                year: 'numeric',
                              })
                            : 'Sin sesiones'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/pacientes/${p.paciente_id}/metricas`);
                            }}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-blue-600 hover:bg-blue-50 border border-blue-200 transition"
                          >
                            <BarChart3 className="w-3.5 h-3.5" />
                            <span>Ver informe</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
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
