export interface User {
  id: string;
  email: string;
  creado_en?: string | null;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterResponse {
  id: string;
  email: string;
  creado_en?: string | null;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
