"""Authentication and authorization utilities."""

import secrets
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from src.infra.config import get_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class AuthService:
    """Service for authentication and authorization."""

    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.jwt_secret_key or "your-secret-key-change-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)


# Global auth service instance
auth_service = AuthService()


class CurrentUser:
    """Current user context."""

    def __init__(self, user_id: UUID, company_id: UUID, email: str, roles: list = None):
        self.user_id = user_id
        self.company_id = company_id
        self.email = email
        self.roles = roles or ["user"]

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.has_role("admin")

    def can_access_company(self, company_id: UUID) -> bool:
        """Check if user can access a specific company."""
        return self.company_id == company_id or self.is_admin()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    user_id = payload.get("sub")
    company_id = payload.get("company_id")
    email = payload.get("email")
    roles = payload.get("roles", ["user"])

    if not user_id or not company_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        user_id=UUID(user_id),
        company_id=UUID(company_id),
        email=email,
        roles=roles
    )


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> CurrentUser | None:
    """Get current user from JWT token (optional)."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """Decorator to require a specific role."""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require admin role."""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


def require_company_access(company_id: UUID):
    """Require access to a specific company."""
    def company_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.can_access_company(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
        return current_user
    return company_checker


# For development/testing - create a simple user
def create_test_user(company_id: UUID = None) -> dict[str, str]:
    """Create a test user for development."""
    if not company_id:
        company_id = UUID("123e4567-e89b-12d3-a456-426614174007")

    user_id = UUID("123e4567-e89b-12d3-a456-426614174008")
    email = "test@example.com"

    token_data = {
        "sub": str(user_id),
        "company_id": str(company_id),
        "email": email,
        "roles": ["user", "admin"]
    }

    token = auth_service.create_access_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user_id),
        "company_id": str(company_id),
        "email": email
    }
