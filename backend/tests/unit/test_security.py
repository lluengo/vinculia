import uuid
from datetime import timedelta
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.domain.exceptions import InvalidTokenException


def test_password_hashing_and_verification():
    raw_password = "SuperSecretPassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_access_token_creation_and_decoding():
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id)

    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_refresh_token_creation_and_decoding():
    user_id = uuid.uuid4()
    token = create_refresh_token(subject=user_id)

    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_token_type_mismatch_raises_exception():
    user_id = uuid.uuid4()
    access_token = create_access_token(subject=user_id)

    with pytest.raises(InvalidTokenException) as exc_info:
        decode_token(access_token, expected_type="refresh")
    assert "Tipo de token inválido" in str(exc_info.value)


def test_expired_token_raises_exception():
    user_id = uuid.uuid4()
    expired_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(seconds=-1)
    )

    with pytest.raises(InvalidTokenException) as exc_info:
        decode_token(expired_token)
    assert "ha expirado" in str(exc_info.value)
