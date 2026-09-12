import os
import sys
from pathlib import Path

# Añadir backend al sys.path para imports limpios
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-only-12345"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:Holamundo1123!@localhost:5432/vinculia"
