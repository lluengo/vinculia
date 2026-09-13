import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { PublicRoute } from './components/PublicRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { PacientesPage } from './pages/PacientesPage';
import { ActividadesPage } from './pages/ActividadesPage';
import { ConfiguradorPage } from './pages/ConfiguradorPage';
import { PlayPage } from './pages/PlayPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Rutas Públicas (sólo accesibles para usuarios NO autenticados) */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* Ruta Pública de Juego (Acceso directo para niños mediante Enlace Único con Token) */}
          <Route path="/play/:token" element={<PlayPage />} />

          {/* Rutas Protegidas (requieren token JWT del profesional) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/pacientes" element={<PacientesPage />} />
            <Route path="/actividades" element={<ActividadesPage />} />
            <Route path="/actividades/nueva" element={<ConfiguradorPage />} />
            <Route path="/actividades/:id/editar" element={<ConfiguradorPage />} />
          </Route>

          {/* Redirección por defecto */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
