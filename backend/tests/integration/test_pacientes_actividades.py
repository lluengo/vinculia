import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def auth_headers() -> dict:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unique_email = f"prof_{uuid.uuid4().hex[:8]}@vinculia.com"
        password = "SecurePassword123!"

        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": password,
                "password_confirm": password,
            },
        )
        assert reg_resp.status_code == 201
        token = reg_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}


async def test_pacientes_crud_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Crear paciente
        create_resp = await client.post(
            "/api/v1/pacientes",
            headers=auth_headers,
            json={"apodo": "Mateo", "edad": 7},
        )
        assert create_resp.status_code == 201
        paciente = create_resp.json()
        assert paciente["apodo"] == "Mateo"
        assert paciente["edad"] == 7
        paciente_id = paciente["id"]

        # 2. Listar pacientes
        list_resp = await client.get("/api/v1/pacientes", headers=auth_headers)
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["total"] >= 1
        assert any(p["id"] == paciente_id for p in list_data["items"])

        # 3. Detalle de paciente
        get_resp = await client.get(f"/api/v1/pacientes/{paciente_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["apodo"] == "Mateo"

        # 4. Actualizar paciente
        update_resp = await client.patch(
            f"/api/v1/pacientes/{paciente_id}",
            headers=auth_headers,
            json={"apodo": "Mateo Actualizado", "edad": 8},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["apodo"] == "Mateo Actualizado"
        assert update_resp.json()["edad"] == 8

        # 5. Eliminar paciente (soft delete)
        del_resp = await client.delete(f"/api/v1/pacientes/{paciente_id}", headers=auth_headers)
        assert del_resp.status_code == 204

        # 6. Paciente eliminado ya no debe encontrarse
        get_after_del = await client.get(f"/api/v1/pacientes/{paciente_id}", headers=auth_headers)
        assert get_after_del.status_code == 404


async def test_actividades_and_public_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Crear un paciente para asociar
        p_resp = await client.post(
            "/api/v1/pacientes",
            headers=auth_headers,
            json={"apodo": "Lucía", "edad": 6},
        )
        assert p_resp.status_code == 201
        paciente_id = p_resp.json()["id"]

        # 1. Crear actividad tipo asociación
        actividad_payload = {
            "paciente_id": paciente_id,
            "tipo_plantilla": "asociacion",
            "titulo": "Asociación de Animales y Hábitats",
            "descripcion": "Une cada animal con su hábitat natural",
            "modo": "imagen-imagen",
            "pares": [
                {
                    "origen_url": "https://example.com/leon.jpg",
                    "destino_url": "https://example.com/sabana.jpg",
                    "es_correcto": True,
                },
                {
                    "origen_url": "https://example.com/pinguino.jpg",
                    "destino_url": "https://example.com/antartida.jpg",
                    "es_correcto": True,
                },
            ],
            "configuracion": {
                "limite_tiempo_seg": 180,
                "nivel_dificultad": 2,
                "tamano_elementos": "mediano",
                "tolerancia_errores": 2,
            },
        }

        act_resp = await client.post(
            "/api/v1/actividades",
            headers=auth_headers,
            json=actividad_payload,
        )
        assert act_resp.status_code == 201
        actividad = act_resp.json()
        actividad_id = actividad["id"]
        assert actividad["titulo"] == "Asociación de Animales y Hábitats"
        assert len(actividad["pares"]) == 2

        # 2. Listar actividades
        list_resp = await client.get(
            f"/api/v1/actividades?paciente_id={paciente_id}",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] >= 1

        # 3. Generar enlace único
        link_resp = await client.post(
            f"/api/v1/actividades/{actividad_id}/enlace",
            headers=auth_headers,
        )
        assert link_resp.status_code == 200
        link_data = link_resp.json()
        assert "token" in link_data
        token = link_data["token"]
        assert link_data["url_completa"] == f"/play/{token}"

        # 4. Obtener actividad pública (SIN headers / sin JWT)
        pub_resp = await client.get(f"/api/v1/publico/actividades/{token}")
        assert pub_resp.status_code == 200
        pub_data = pub_resp.json()
        assert pub_data["titulo"] == "Asociación de Animales y Hábitats"
        assert pub_data["apodo_paciente"] == "Lucía"
        assert len(pub_data["pares"]) == 2

        # 5. Registrar resultado de sesión pública
        sesion_resp = await client.post(
            "/api/v1/publico/sesiones",
            json={
                "actividad_id": actividad_id,
                "token": token,
                "tiempo_segundos": 45,
                "aciertos": 2,
                "errores": 0,
            },
        )
        assert sesion_resp.status_code == 201
        assert "id" in sesion_resp.json()
