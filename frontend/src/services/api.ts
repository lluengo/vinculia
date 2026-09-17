import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { RefreshTokenResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
export const BACKEND_URL = API_BASE_URL.replace('/api/v1', '');

export const resolveMediaUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:') || url.startsWith('blob:')) {
    return url;
  }
  if (url.startsWith('/')) {
    return `${BACKEND_URL}${url}`;
  }
  return url;
};

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Request para adjuntar el Access Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de Response para manejar renovación automática con Refresh Token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si es error 401 y no es la ruta de login o refresh
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/register') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post<RefreshTokenResponse>(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        localStorage.setItem('access_token', data.access_token);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        }

        processQueue(null, data.access_token);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Endpoints de Pacientes
export const getPacientes = async (page = 1, size = 10) => {
  const response = await api.get(`/pacientes?page=${page}&size=${size}`);
  return response.data;
};

export const getPaciente = async (id: string) => {
  const response = await api.get(`/pacientes/${id}`);
  return response.data;
};

export const createPaciente = async (data: { apodo: string; edad?: number | null }) => {
  const response = await api.post('/pacientes', data);
  return response.data;
};

export const updatePaciente = async (id: string, data: { apodo?: string; edad?: number | null }) => {
  const response = await api.patch(`/pacientes/${id}`, data);
  return response.data;
};

export const deletePaciente = async (id: string) => {
  const response = await api.delete(`/pacientes/${id}`);
  return response.data;
};

// Endpoints de Actividades
export const getActividades = async (params?: { paciente_id?: string; tipo?: string; page?: number; size?: number }) => {
  const response = await api.get('/actividades', { params });
  return response.data;
};

export const getActividad = async (id: string) => {
  const response = await api.get(`/actividades/${id}`);
  return response.data;
};

export const createActividad = async (data: any) => {
  const response = await api.post('/actividades', data);
  return response.data;
};

export const updateActividad = async (id: string, data: any) => {
  const response = await api.patch(`/actividades/${id}`, data);
  return response.data;
};

export const deleteActividad = async (id: string) => {
  const response = await api.delete(`/actividades/${id}`);
  return response.data;
};

export const generarEnlace = async (id: string) => {
  const response = await api.post(`/actividades/${id}/enlace`);
  return response.data;
};

export const subirAssets = async (id: string, formData: FormData) => {
  const response = await api.post(`/actividades/${id}/assets`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// Endpoints Públicos (para pacientes / juego)
export const getActividadPublica = async (token: string) => {
  const response = await api.get(`/publico/actividades/${token}`);
  return response.data;
};

export const crearSesionPublica = async (data: {
  actividad_id?: string;
  token?: string;
  tiempo_segundos: number;
  aciertos: number;
  errores: number;
}) => {
  const response = await api.post('/publico/sesiones', data);
  return response.data;
};

// Endpoints de Métricas y Evaluación
export const getResumenPaciente = async (pacienteId: string) => {
  const response = await api.get(`/metricas/paciente/${pacienteId}/resumen`);
  return response.data;
};

export const getEvolucionPaciente = async (
  pacienteId: string,
  params?: { desde?: string; hasta?: string; agrupacion?: 'dia' | 'semana' }
) => {
  const response = await api.get(`/metricas/paciente/${pacienteId}/evolucion`, { params });
  return response.data;
};

export const getRendimientoPorActividad = async (pacienteId: string) => {
  const response = await api.get(`/metricas/paciente/${pacienteId}/por-actividad`);
  return response.data;
};

export const exportarSesionesCSV = async (pacienteId: string, apodo: string = 'paciente') => {
  const response = await api.get(`/metricas/paciente/${pacienteId}/export?formato=csv`, {
    responseType: 'blob',
  });
  // Disparar descarga automática en el navegador
  const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `paciente_${apodo.replace(/\s+/g, '_')}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getGlobalResumen = async () => {
  const response = await api.get('/metricas/global/resumen');
  return response.data;
};

export const getRankingPacientes = async (orden: 'progreso' | 'actividad' = 'progreso') => {
  const response = await api.get(`/metricas/global/ranking-pacientes?orden=${orden}`);
  return response.data;
};

