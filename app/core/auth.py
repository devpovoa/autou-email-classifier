"""
JWT Authentication and Security module for AutoU Email Classifier.

This module provides JWT token generation, validation, and API key
authentication to secure the email classification endpoints.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# Pydantic models for JWT
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []


class User(BaseModel):
    username: str
    email: Optional[str] = None
    is_active: bool = True
    scopes: list[str] = []


class UserInDB(User):
    hashed_password: str


# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


# Default users for demonstration (in production, use database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@autou.com",
        "hashed_password": pwd_context.hash("admin123"),
        "is_active": True,
        "scopes": ["classify:read", "classify:write", "admin"],
    },
    "api_user": {
        "username": "api_user",
        "email": "api@autou.com",
        "hashed_password": pwd_context.hash("apiuser123"),
        "is_active": True,
        "scopes": ["classify:read", "classify:write"],
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password."""
    user_dict = fake_users_db.get(username)
    if not user_dict:
        return None

    user = UserInDB(**user_dict)
    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        username: str = payload.get("sub")
        if username is None:
            return None

        token_scopes = payload.get("scopes", [])
        return {
            "username": username,
            "scopes": token_scopes,
            "exp": payload.get("exp"),
        }

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise credentials_exception

    username = token_data.get("username")
    if not username:
        raise credentials_exception

    user_dict = fake_users_db.get(username)
    if not user_dict:
        raise credentials_exception

    user = User(**user_dict)
    user.scopes = token_data.get("scopes", [])

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def verify_api_key(api_key: str) -> bool:
    """Verify API key (simple implementation)."""
    if not settings.default_api_key:
        return False

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(api_key, settings.default_api_key)


async def api_key_auth(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """API Key authentication dependency."""
    if not settings.enable_auth:
        return "api_key_disabled"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required"
        )

    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return api_key


def require_scopes(*required_scopes: str):
    """Decorator to require specific scopes for endpoint access."""

    def scope_checker(current_user: User = Depends(get_current_active_user)):
        if not any(scope in current_user.scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return scope_checker


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


# Rate limiting (simple in-memory implementation)
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=settings.rate_limit_window)

        if identifier not in self.requests:
            self.requests[identifier] = []

        # Clean old requests
        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if req_time > window_start
        ]

        # Check rate limit
        if len(self.requests[identifier]) >= settings.rate_limit_requests:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_check(
    current_user: Optional[User] = Depends(get_current_user),
):
    """Rate limiting dependency."""
    identifier = current_user.username if current_user else "anonymous"

    if not rate_limiter.is_allowed(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    return True
