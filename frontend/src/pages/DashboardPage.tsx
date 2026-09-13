import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, ShieldCheck, Activity, Users, Calendar } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header / Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm">
              V
            </div>
            <div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">Vinculia</span>
              <span className="hidden sm:inline-block ml-2 px-2.5 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 rounded-full border border-blue-200">
                Panel Profesional
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-sm font-semibold text-slate-900">{user?.email}</span>
              <span className="text-xs text-slate-500">Terapeuta / Especialista</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 border border-slate-300 rounded-xl text-sm font-semibold text-slate-700 hover:bg-red-50 hover:text-red-700 hover:border-red-200 transition-all cursor-pointer"
              title="Cerrar sesión"
            >
              <LogOut className="w-4 h-4" />
              <span>Cerrar sesión</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Welcome Banner */}
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm mb-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 text-emerald-600 font-semibold text-sm mb-2">
                <ShieldCheck className="w-5 h-5" />
                <span>Sesión autenticada con JWT (Access + Refresh Token)</span>
              </div>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                Bienvenido {user?.email}
              </h1>
              <p className="mt-2 text-slate-600 max-w-2xl text-base">
                Has ingresado correctamente a la plataforma. Desde este panel podrás gestionar tus
                pacientes bajo estricto cumplimiento GDPR/ARCO y configurar actividades de estimulación cognitiva.
              </p>
            </div>
          </div>
        </div>

        {/* Profile Card & Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                <User className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Identificador UUID</p>
                <p className="text-sm font-mono font-bold text-slate-800 break-all">{user?.id}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-emerald-600">
                <Calendar className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Fecha de Creación</p>
                <p className="text-sm font-medium text-slate-800">
                  {user?.creado_en ? new Date(user.creado_en).toLocaleString('es-ES') : 'Reciente'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-purple-600">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Estado de Cuenta</p>
                <p className="text-sm font-bold text-emerald-600">Activo y Verificado</p>
              </div>
            </div>
          </div>
        </div>

        {/* Next MVP Modules Preview */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-8 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-2 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-600" />
            Próximos módulos a integrar en el MVP
          </h2>
          <p className="text-slate-600 text-sm mb-6">
            Los siguientes bloques del sistema ya tienen sus tablas mapeadas en la base de datos y están listos para implementarse:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/pacientes')}
              className="bg-white p-5 rounded-xl border border-blue-100 shadow-sm hover:shadow-md hover:border-blue-400 transition text-left cursor-pointer group"
            >
              <h3 className="font-bold text-slate-800 text-sm group-hover:text-blue-600 transition">
                1. Gestión de Pacientes ➔
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Registra y administra las fichas de los niños con seudónimos y edades (cumplimiento GDPR).
              </p>
            </button>
            <button
              onClick={() => navigate('/actividades')}
              className="bg-white p-5 rounded-xl border border-blue-100 shadow-sm hover:shadow-md hover:border-blue-400 transition text-left cursor-pointer group"
            >
              <h3 className="font-bold text-slate-800 text-sm group-hover:text-blue-600 transition">
                2. Plantillas de Ejercicios ➔
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Diseña ejercicios de asociación, ajusta dificultad táctil y genera enlaces únicos para el juego.
              </p>
            </button>
          </div>

        </div>
      </main>
    </div>
  );
};
