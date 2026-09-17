export interface Paciente {
  id: string;
  profesional_id?: string;
  apodo: string;
  edad?: number | null;
  creado_en?: string;
  eliminado_en?: string | null;
  ultima_sesion?: string | null;
}

export interface Par {
  origen_url: string;
  destino_url: string;
  es_correcto: boolean;
}

export interface Configuracion {
  limite_tiempo_seg: number;
  nivel_dificultad: number;
  tamano_elementos: string;
  tolerancia_errores: number;
}

export interface Actividad {
  id: string;
  profesional_id?: string;
  paciente_id?: string | null;
  tipo_plantilla: string;
  titulo: string;
  descripcion?: string | null;
  modo: string;
  pares: Par[];
  configuracion: Configuracion;
  token_acceso?: string | null;
  expira_en?: string | null;
  activa: boolean;
  eliminado_en?: string | null;
  creado_en?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface EnlaceResponse {
  token: string;
  url_completa: string;
  expira_en: string;
}

export interface ActividadPublica {
  id: string;
  titulo: string;
  descripcion?: string | null;
  modo: string;
  pares: Par[];
  configuracion: Configuracion;
  apodo_paciente?: string | null;
}

export interface PacienteInfo {
  id: string;
  apodo: string;
  edad?: number | null;
}

export interface UltimaSesion {
  fecha?: string | null;
  tiempo: number;
  aciertos: number;
  errores: number;
}

export interface PacienteResumenMetricas {
  paciente: PacienteInfo;
  total_sesiones: number;
  tiempo_promedio_seg: number;
  tasa_acierto_promedio: number;
  ultima_sesion?: UltimaSesion | null;
  tendencia: 'mejora' | 'estable' | 'retroceso' | 'sin_datos';
}

export interface EvolucionItem {
  fecha: string;
  sesiones: number;
  tiempo_promedio: number;
  tasa_acierto: number;
}

export interface RendimientoActividad {
  actividad_id?: string | null;
  titulo: string;
  sesiones: number;
  tiempo_promedio: number;
  tasa_acierto: number;
}

export interface GlobalResumen {
  total_pacientes: number;
  total_sesiones: number;
  total_actividades: number;
  tasa_acierto_promedio: number;
  pacientes_activos_ultimos_7_dias: number;
}

export interface RankingPacienteItem {
  paciente_id: string;
  apodo: string;
  edad?: number | null;
  total_sesiones: number;
  tasa_acierto_promedio: number;
  tendencia: 'mejora' | 'estable' | 'retroceso' | 'sin_datos';
  ultima_sesion?: string | null;
}
