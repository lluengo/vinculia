from fastapi import APIRouter
from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.pacientes import router as pacientes_router
from app.presentation.api.v1.endpoints.actividades import router as actividades_router
from app.presentation.api.v1.endpoints.publico import router as publico_router
from app.presentation.api.v1.endpoints.metricas import router as metricas_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(pacientes_router)
api_router.include_router(actividades_router)
api_router.include_router(publico_router)
api_router.include_router(metricas_router)
