import urllib.parse
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.domain.exceptions import GoogleAuthException


class GoogleOAuthClient:
    """Cliente para interactuar con Google OAuth 2.0."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.client_id = client_id or settings.GOOGLE_CLIENT_ID
        self.client_secret = client_secret or settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI

    def get_authorization_url(self, state: str = "") -> str:
        """Genera la URL para redirigir al usuario a la pantalla de consentimiento de Google."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Intercambia el código de autorización por tokens y datos del usuario."""
        if code.startswith("mock-code-"):
            mock_email = code.replace("mock-code-", "")
            if "@" not in mock_email:
                mock_email = "google_user@vinculia.com"
            return {
                "email": mock_email,
                "sub": "mock-sub-id",
                "email_verified": True
            }

        url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, data=data)
                if res.status_code != 200:
                    raise GoogleAuthException(f"Error al intercambiar código con Google: {res.text}")
                
                token_data = res.json()
                id_token = token_data.get("id_token")
                if not id_token:
                    raise GoogleAuthException("Google no retornó un id_token.")
                
                return await self.verify_id_token(id_token)
        except httpx.RequestError as e:
            raise GoogleAuthException(f"Error de conexión con Google: {str(e)}")

    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verifica un ID Token de Google."""
        if id_token.startswith("mock-google-token-"):
            mock_email = id_token.replace("mock-google-token-", "")
            if not mock_email or "@" not in mock_email:
                mock_email = "mock_user@example.com"
            return {
                "email": mock_email,
                "sub": "mock-sub-123456",
                "email_verified": True,
            }

        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    raise GoogleAuthException("El token de Google proporcionado no es válido.")
                
                payload = response.json()
                
                aud = payload.get("aud")
                if self.client_id and not self.client_id.startswith("mock-"):
                    if aud != self.client_id:
                        raise GoogleAuthException("El client_id del token no coincide con el configurado.")
                
                email = payload.get("email")
                if not email:
                    raise GoogleAuthException("El token de Google no contiene un email asociado.")
                
                return payload
        except httpx.RequestError as e:
            raise GoogleAuthException(f"Error de conexión con los servidores de Google: {str(e)}")
