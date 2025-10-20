"""Authentication API router."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import structlog

from src.app.auth import auth_service, get_current_user, CurrentUser, create_test_user
from src.app.dto import ErrorResponse

logger = structlog.get_logger()
router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str
    user_id: str
    company_id: str
    email: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint (placeholder for now)."""
    try:
        # For now, this is a placeholder implementation
        # In a real system, you would:
        # 1. Validate credentials against a user database
        # 2. Check if user is active
        # 3. Return appropriate tokens
        
        # For development, we'll create a test user
        if request.email == "test@example.com" and request.password == "password":
            test_user = create_test_user()
            return LoginResponse(**test_user)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", email=request.email, error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(current_user: CurrentUser = Depends(get_current_user)):
    """Refresh access token."""
    try:
        # Create new token with same user data
        token_data = {
            "sub": str(current_user.user_id),
            "company_id": str(current_user.company_id),
            "email": current_user.email,
            "roles": current_user.roles
        }
        
        new_token = auth_service.create_access_token(token_data)
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer"
        )
        
    except Exception as e:
        logger.error("Token refresh failed", user_id=str(current_user.user_id), error=str(e))
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.get("/auth/me")
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": str(current_user.user_id),
        "company_id": str(current_user.company_id),
        "email": current_user.email,
        "roles": current_user.roles
    }


@router.post("/auth/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    """Logout endpoint (placeholder)."""
    # In a real system, you might:
    # 1. Add token to a blacklist
    # 2. Invalidate refresh tokens
    # 3. Log the logout event
    
    logger.info("User logged out", user_id=str(current_user.user_id))
    return {"message": "Successfully logged out"}


@router.post("/auth/test-token")
async def create_test_token():
    """Create a test token for development (remove in production)."""
    test_user = create_test_user()
    return test_user
