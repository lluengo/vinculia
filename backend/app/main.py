import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.presentation.api.v1.router import api_router

# Configuración de Logging estructurado con Loguru
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

tags_metadata = [
    {
        "name": "Auth",
        "description": "Operaciones de autenticación, registro, login, refresh token, logout y Google OAuth.",
    },
    {
        "name": "Profesionales",
        "description": "Gestión y consulta del perfil del profesional.",
    },
    {
        "name": "Sistema",
        "description": "Monitoreo del estado y salud de la API.",
    }
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la plataforma SaaS multidisciplinaria Vinculia (estimulación cognitiva y motora)",
    version="1.0.0",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS para Frontend Vite (http://localhost:5173)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Endpoint de salud del sistema
@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)
