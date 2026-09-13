import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  Users,
  LayoutTemplate,
  BarChart3,
  Link as LinkIcon,
  LogOut,
  Menu,
  ChevronRight,
  BrainCircuit,
} from 'lucide-react';


interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/pacientes', label: 'Mis Pacientes', icon: Users },
    { to: '/actividades', label: 'Plantillas de Ejercicios', icon: LayoutTemplate },
    { to: '/dashboard', label: 'Métricas de Progreso', icon: BarChart3 },
    { to: '/actividades', label: 'Enlaces Únicos', icon: LinkIcon },
  ];

  return (
    <div className="flex h-screen bg-[#F8FAFC] font-sans antialiased overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`bg-[#1E293B] text-white flex flex-col transition-all duration-300 ease-in-out ${
          collapsed ? 'w-20' : 'w-64'
        } shadow-xl z-20`}
      >
        {/* Logo Brand */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-700/50">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="p-2 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <BrainCircuit className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <span className="font-bold text-xl tracking-tight text-white whitespace-nowrap">
                Vinculia
              </span>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title={collapsed ? 'Expandir menú' : 'Colapsar menú'}
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.label}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-3 py-3 rounded-xl text-sm font-medium transition-colors group ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                  }`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && (
                  <span className="ml-3 font-medium whitespace-nowrap">{item.label}</span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User Info & Logout in Sidebar */}
        <div className="p-4 border-t border-slate-700/50 bg-slate-900/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="w-9 h-9 rounded-full bg-blue-500/20 text-blue-400 font-semibold flex items-center justify-center flex-shrink-0 border border-blue-500/30">
                {user?.email ? user.email.charAt(0).toUpperCase() : 'P'}
              </div>
              {!collapsed && (
                <div className="overflow-hidden">
                  <p className="text-sm font-semibold text-white truncate">
                    {user?.email?.split('@')[0] || 'Profesional'}
                  </p>
                  <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                </div>
              )}
            </div>
            {!collapsed && (
              <button
                onClick={handleLogout}
                className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition"
                title="Cerrar sesión"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Wrapper */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between shadow-sm z-10">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-800">Panel Multidisciplinario</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="inline-block w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-xs font-semibold text-slate-500">Servicio Activo</span>
            </div>
            <div className="h-6 w-px bg-slate-200"></div>
            <div className="text-sm text-slate-600 font-medium">{user?.email}</div>
          </div>
        </header>

        {/* Page Content Container */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#F8FAFC]">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
};
