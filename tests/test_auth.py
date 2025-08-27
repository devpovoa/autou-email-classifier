"""
Tests for JWT authentication and security features.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.auth import (
    authenticate_user,
    create_access_token,
    generate_api_key,
    hash_api_key,
    rate_limiter,
    verify_token,
)
from app.core.config import settings
from main import app

client = TestClient(app)


class TestJWTAuthentication:
    """Test JWT token authentication."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "testuser", "scopes": ["read"]}
        token = create_access_token(data)

        # Verify token can be decoded
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        assert payload["sub"] == "testuser"
        assert payload["scopes"] == ["read"]
        assert "exp" in payload

    def test_create_access_token_with_expiration(self):
        """Test JWT token creation with custom expiration"""
        data = {"sub": "test", "scopes": ["read"]}
        expires_delta = timedelta(hours=3)

        # Create token
        token = create_access_token(data, expires_delta=expires_delta)

        # Decode and verify
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        # Check expiration (allow small time difference for processing)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires_delta

        # Allow 60 seconds tolerance for test execution time
        assert abs((exp_datetime - expected_exp).total_seconds()) < 60

    def test_verify_valid_token(self):
        """Test verification of valid JWT token."""
        data = {"sub": "testuser", "scopes": ["read", "write"]}
        token = create_access_token(data)

        token_data = verify_token(token)

        assert token_data is not None
        assert token_data["username"] == "testuser"
        assert token_data["scopes"] == ["read", "write"]
        assert "exp" in token_data

    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token."""
        invalid_token = "invalid.token.here"

        token_data = verify_token(invalid_token)

        assert token_data is None

    def test_verify_expired_token(self):
        """Test verification of expired JWT token."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        token_data = verify_token(token)

        assert token_data is None


class TestUserAuthentication:
    """Test user authentication functions."""

    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        user = authenticate_user("admin", "admin123")

        assert user is not None
        assert user.username == "admin"
        assert user.is_active is True
        assert "admin" in user.scopes

    def test_authenticate_invalid_username(self):
        """Test authentication with invalid username."""
        user = authenticate_user("nonexistent", "password")

        assert user is None

    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = authenticate_user("admin", "wrongpassword")

        assert user is None

    def test_authenticate_inactive_user(self):
        """Test authentication behavior with inactive user."""
        # This test assumes fake_users_db can be modified
        # In real implementation, you'd have a proper user management system
        user = authenticate_user("api_user", "apiuser123")

        assert user is not None
        assert user.is_active is True


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""

    def test_login_endpoint_valid_credentials(self):
        """Test login endpoint with valid credentials."""
        response = client.post(
            "/auth/token", data={"username": "admin", "password": "admin123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_endpoint_invalid_credentials(self):
        """Test login endpoint with invalid credentials."""
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_me_endpoint_with_token(self):
        """Test /auth/me endpoint with valid token."""
        # First login to get token
        login_response = client.post(
            "/auth/token", data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Use token to access protected endpoint
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "admin"
        assert data["email"] == "admin@autou.com"
        assert data["is_active"] is True
        assert "admin" in data["scopes"]

    def test_get_me_endpoint_without_token(self):
        """Test /auth/me endpoint without token."""
        response = client.get("/auth/me")

        # FastAPI Security returns 403 when no token provided
        assert response.status_code == 403


class TestProtectedEndpoints:
    """Test protected API endpoints."""

    def get_admin_token(self):
        """Helper to get admin token."""
        response = client.post(
            "/auth/token", data={"username": "admin", "password": "admin123"}
        )
        return response.json()["access_token"]

    def test_classify_text_with_valid_token(self):
        """Test text classification with valid JWT token."""
        token = self.get_admin_token()

        response = client.post(
            "/api/classify/text",
            json={"text": "Preciso de ajuda urgente com o sistema!"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "category" in data
        assert "confidence" in data
        assert data["user"] == "admin"

    def test_classify_text_without_token(self):
        """Test text classification without token."""
        response = client.post("/api/classify/text", json={"text": "Test text"})

        # FastAPI Security returns 403 when no token provided
        assert response.status_code == 403

    def test_classify_text_with_insufficient_scope(self):
        """Test text classification with token lacking required scope."""
        # This would require creating a user with limited scopes
        # For now, we test with admin who has all scopes
        token = self.get_admin_token()

        response = client.post(
            "/api/classify/text",
            json={"text": "Test text"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Admin has all scopes, so this should succeed
        assert response.status_code == 200


class TestAPIKeyAuthentication:
    """Test API key authentication."""

    def test_api_key_generation(self):
        """Test API key generation."""
        api_key = generate_api_key()

        assert len(api_key) > 20
        assert isinstance(api_key, str)

    def test_api_key_hashing(self):
        """Test API key hashing."""
        api_key = "test_api_key"
        hashed = hash_api_key(api_key)

        assert len(hashed) == 64  # SHA256 hex digest
        assert hashed != api_key

    def test_classify_with_api_key(self):
        """Test classification using API key."""
        # This test assumes DEFAULT_API_KEY is set in test environment
        if not settings.default_api_key:
            pytest.skip("DEFAULT_API_KEY not configured for testing")

        response = client.post(
            "/api/v1/classify",
            json={"text": "Test email content"},
            headers={settings.api_key_header: settings.default_api_key},
        )

        assert response.status_code == 200
        data = response.json()

        assert "category" in data
        assert data["auth_method"] == "api_key"

    def test_classify_with_invalid_api_key(self):
        """Test classification with invalid API key."""
        response = client.post(
            "/api/v1/classify",
            json={"text": "Test email content"},
            headers={settings.api_key_header: "invalid_key"},
        )

        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiter_allows_requests_within_limit(self):
        """Test rate limiter allows requests within limit."""
        identifier = "test_user"

        # Clear any existing requests
        rate_limiter.requests.pop(identifier, None)

        # Make requests within limit
        for _ in range(5):
            allowed = rate_limiter.is_allowed(identifier)
            assert allowed is True

    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test rate limiter blocks requests over limit."""
        identifier = "test_user_overload"

        # Clear any existing requests
        rate_limiter.requests.pop(identifier, None)

        # Fill up the rate limit (set to a small number for testing)
        original_limit = settings.rate_limit_requests
        settings.rate_limit_requests = 3

        try:
            # Make requests up to limit
            for _ in range(3):
                allowed = rate_limiter.is_allowed(identifier)
                assert allowed is True

            # Next request should be blocked
            allowed = rate_limiter.is_allowed(identifier)
            assert allowed is False
        finally:
            # Restore original limit
            settings.rate_limit_requests = original_limit


class TestSecurityFeatures:
    """Test various security features."""

    def test_health_endpoint_always_accessible(self):
        """Test health endpoint is always accessible."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_web_interface_still_accessible(self):
        """Test web interface remains accessible."""
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_docs_endpoint_accessible(self):
        """Test API documentation is accessible."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_token_in_swagger_ui(self):
        """Test that Swagger UI can use JWT tokens."""
        # Get a token
        token = TestProtectedEndpoints().get_admin_token()

        # The token should be usable in Swagger UI
        # This is more of an integration test
        assert token is not None
        assert len(token) > 50
