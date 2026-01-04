import pytest
from datetime import timedelta


def test_create_access_token():
    """Test access token creation."""
    from moana.utils.security import create_access_token

    token = create_access_token(data={"sub": "user123"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    """Test access token decoding."""
    from moana.utils.security import create_access_token, decode_access_token

    token = create_access_token(data={"sub": "user123", "name": "Test"})
    payload = decode_access_token(token)

    assert payload["sub"] == "user123"
    assert payload["name"] == "Test"


def test_expired_token():
    """Test expired token raises error."""
    from moana.utils.security import create_access_token, decode_access_token

    token = create_access_token(
        data={"sub": "user123"},
        expires_delta=timedelta(seconds=-1),  # Already expired
    )

    payload = decode_access_token(token)
    assert payload is None


def test_invalid_token():
    """Test invalid token returns None."""
    from moana.utils.security import decode_access_token

    payload = decode_access_token("invalid.token.here")
    assert payload is None


def test_create_refresh_token():
    """Test refresh token creation."""
    from moana.utils.security import create_refresh_token, decode_access_token

    token = create_refresh_token(data={"sub": "user123"})
    payload = decode_access_token(token)

    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"
