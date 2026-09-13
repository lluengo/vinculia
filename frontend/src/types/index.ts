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
