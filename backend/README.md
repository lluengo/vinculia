# Vinculia Backend - Módulo de Autenticación y Perfiles

Backend desarrollado en **FastAPI** bajo los principios de **Clean Architecture / Arquitectura Hexagonal**.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/                         # Configuración, seguridad (JWT/bcrypt) y base de datos
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── domain/                       # Capa de Dominio pura (sin dependencias de frameworks)
│   │   ├── models/                   # Entidades de dominio (Profesional)
│   │   ├── exceptions.py             # Excepciones de dominio
│   │   └── ports/                    # Interfaces de repositorio (ProfesionalRepositoryPort)
│   ├── application/                  # Capa de Aplicación (Casos de uso y DTOs)
│   │   ├── dtos/                     # Esquemas Pydantic v2 (Register, Login, Tokens, etc.)
│   │   └── use_cases/                # Lógica de negocio (Register, Login, Refresh, Me, Google)
│   ├── infrastructure/               # Capa de Infraestructura (Adaptadores externos)
│   │   ├── db/
│   │   │   ├── models/               # Modelos SQLAlchemy 2.0 mapeando esquema existente
│   │   │   └── repositories/         # SqlProfesionalRepository
│   │   └── oauth/                    # Google OAuth client
│   ├── presentation/                 # Capa de Presentación (FastAPI)
│   │   └── api/
│   │       └── v1/
│   │           ├── endpoints/        # Endpoints REST (/register, /login, /refresh, /me, /google)
│   │           ├── dependencies.py   # Inyección de dependencias
│   │           └── router.py
│   └── main.py                       # Aplicación FastAPI, CORS y middlewares
├── tests/
│   ├── conftest.py
│   ├── unit/                         # Tests unitarios
│   └── integration/                  # Tests end-to-end contra PostgreSQL real
├── requirements.txt
├── .env.example
└── .env
```

## Configuración y Ejecución

### 1. Activar Entorno Virtual
```bash
cd backend
source .venv/bin/activate
```

### 2. Iniciar Servidor de Desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```
La documentación interactiva de Swagger estará disponible en:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### 3. Ejecutar Pruebas
```bash
pytest -v
```

## Endpoints Disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Verificación de estado del servidor |
| `POST` | `/api/v1/auth/register` | Registro de profesional (email y contraseña) |
| `POST` | `/api/v1/auth/login` | Inicio de sesión (retorna access y refresh tokens) |
| `POST` | `/api/v1/auth/refresh` | Renovación de tokens con refresh_token |
| `GET` | `/api/v1/auth/me` | Obtiene el perfil del profesional autenticado (Bearer token) |
| `POST` | `/api/v1/auth/google` | Inicio de sesión / registro automático con Google OAuth |
