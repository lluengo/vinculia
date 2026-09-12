import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_full_auth_flow_e2e_with_database():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generar un email único para evitar colisiones en la DB real
        unique_email = f"prof_{uuid.uuid4().hex[:8]}@vinculia.com"
        password = "SecurePassword123!"

        # 1. Fallo en registro si contraseñas no coinciden (422)
        mismatch_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": password,
                "password_confirm": "DifferentPassword123!"
            }
        )
        assert mismatch_resp.status_code == 422

        # 2. Registro exitoso
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": password,
                "password_confirm": password
            }
        )
        assert reg_response.status_code == 201
        reg_data = reg_response.json()
        assert reg_data["email"] == unique_email
        assert "access_token" in reg_data
        assert "refresh_token" in reg_data

        # 3. Intento de registro duplicado (debe retornar 409 Conflict)
        dup_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": password,
                "password_confirm": password
            }
        )
        assert dup_response.status_code == 409

        # 4. Login con credenciales válidas
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        assert login_data["expires_in"] == 1800
        assert login_data["user"]["email"] == unique_email

        # 5. Login con credenciales inválidas (debe retornar 401 Unauthorized)
        bad_login = await client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "WrongPassword123!"}
        )
        assert bad_login.status_code == 401

        # 6. Obtener perfil con Bearer token en /auth/me
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == unique_email

        # 7. Intentar /auth/me sin token (debe retornar 401)
        unauth_me = await client.get("/api/v1/auth/me")
        assert unauth_me.status_code == 401

        # 8. Renovar token con /auth/refresh
        refresh_resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert "access_token" in new_tokens
        assert new_tokens["expires_in"] == 1800

        # 9. Cerrar sesión (/auth/logout)
        logout_resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token}
        )
        assert logout_resp.status_code == 200

        # 10. Intentar renovar con token revocado (debe fallar 401)
        failed_refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert failed_refresh.status_code == 401

        # 11. Google OAuth login redirect
        google_login_resp = await client.get(
            "/api/v1/auth/google/login",
            follow_redirects=False
        )
        assert google_login_resp.status_code == 307
        assert "accounts.google.com" in google_login_resp.headers["location"]

        # 12. Google OAuth callback
        google_cb_resp = await client.get(
            "/api/v1/auth/google/callback",
            params={"code": "mock-code-prof_google@vinculia.com"}
        )
        assert google_cb_resp.status_code == 200
        cb_tokens = google_cb_resp.json()
        assert "access_token" in cb_tokens
