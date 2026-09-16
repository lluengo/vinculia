# Vinculia - Plataforma Multidisciplinaria SaaS

Plataforma SaaS para profesionales (psicomotricistas, psicólogos, psicopedagogos, fonoaudiólogos) orientada a la estimulación cognitiva y motora en niños con necesidades especiales.

---

## 🏛️ Arquitectura del Sistema

El proyecto sigue los principios de **Clean Architecture / Arquitectura Hexagonal**:

```
vinculia/
├── backend/                  # API REST con FastAPI y Python 3.13+
│   ├── app/
│   │   ├── core/             # Configuración, JWT (access/refresh), bcrypt (rounds=12), async DB
│   │   ├── domain/           # Entidad Profesional, excepciones, puertos abstractos
│   │   ├── application/      # Casos de uso y esquemas Pydantic v2 con ejemplos
│   │   ├── infrastructure/   # SQLAlchemy 2.0 (async), Postgres (Docker), Google OAuth
│   │   ├── presentation/     # Endpoints REST (/auth/*), OAuth2PasswordBearer, Swagger tags
│   │   └── main.py           # Logging estructurado con Loguru, CORS y /health
│   ├── tests/                # 20 tests con pytest + httpx AsyncClient (unit + integración)
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env
└── frontend/                 # Single Page Application con React 18 + Vite + TypeScript
    ├── src/
    │   ├── components/       # ProtectedRoute, PublicRoute
    │   ├── context/          # AuthContext con Context API
    │   ├── hooks/            # useAuth
    │   ├── pages/            # LoginPage, RegisterPage, DashboardPage
    │   ├── services/         # Axios con interceptor automático para Refresh Token
    │   └── types/            # Tipos e interfaces TypeScript
    ├── tailwind.config.js    # Paleta corporativa (#F8FAFC, #2563EB, #10B981)
    ├── package.json
    └── .env
```

---

## 🚀 Guía de Inicio Rápido

### Prerrequisitos
1. **Docker:** Contenedor `postgres-db` en ejecución (`localhost:5432` con la base de datos `vinculia`).
2. **Python 3.11+**: (`backend/.venv`).
3. **Node.js 18+ y npm**: (`frontend/node_modules`).

---

### 1. Iniciar el Backend (FastAPI)

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

* **API Base:** `http://localhost:8000`
* **Swagger UI interactivo:** `http://localhost:8000/docs` (o `http://localhost:8000/api/v1/docs`)
* **ReDoc:** `http://localhost:8000/redoc`

---

### 2. Iniciar el Frontend (React + Vite)

En una nueva terminal:

```bash
cd frontend
npm run dev
```

* **Aplicación Web:** `http://localhost:5173`

---

## 🧪 Pruebas Automatizadas

### Backend (Pytest)
```bash
cd backend
source .venv/bin/activate
pytest -v
```
* **20/20 tests aprobados:**
  - Hashing seguro con `bcrypt` (factor de coste `rounds=12`).
  - Creación, decodificación y expiración de tokens JWT.
  - Validación de contraseñas fuertes (mayúsculas, números, caracteres especiales).
  - Casos de uso de Registro, Login, Renovación, Logout (Blacklist) y Google OAuth.
  - Test de integración End-to-End contra el contenedor real de PostgreSQL.

### Frontend (Build de Producción)
```bash
cd frontend
npm run build
```

---

## 🔄 Flujo de Prueba End-to-End (Paso a Paso)

1. **Abrir la app en el navegador:**
   Ingresa a [http://localhost:5173](http://localhost:5173). Serás redirigido automáticamente a `/login`.

2. **Registro con validaciones en vivo:**
   * Haz clic en **"Regístrate aquí"** (`/register`).
   * Escribe tu correo electrónico (ej. `terapeuta@vinculia.com`).
   * Observa el panel de **Requisitos de seguridad en tiempo real**: los indicadores se pintan de verde a medida que cumples:
     - Mínimo 8 caracteres
     - Al menos una letra mayúscula
     - Al menos un número
     - Al menos un símbolo especial (`!@#$%^&*`)
     - Confirmación exacta de contraseña
   * Presiona **"Registrarse"**. El usuario se crea en PostgreSQL y se redirige automáticamente al Dashboard.

3. **Acceso al Dashboard protegido:**
   * La ruta `/dashboard` verifica el JWT mediante `ProtectedRoute`.
   * Muestra la bienvenida personalizada: **"Bienvenido {email}"**.
   * Muestra el identificador UUID del profesional y la fecha de creación de la cuenta.

4. **Cierre de sesión seguro:**
   * Haz clic en **"Cerrar sesión"**.
   * El cliente invoca `POST /api/v1/auth/logout`, enviando el refresh token para invalidarlo en la blacklist en memoria del servidor y elimina las credenciales locales.
   * La aplicación redirige a `/login`.

5. **Renovación automática de tokens:**
   * El cliente Axios en `src/services/api.ts` intercepta cualquier error 401 por expiración del `access_token`, solicita un nuevo token a `/api/v1/auth/refresh` con el `refresh_token` de forma transparente y reintenta la petición sin desconectar al usuario.
