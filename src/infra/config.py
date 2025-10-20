"""Application configuration."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    
    # MinIO/S3
    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(..., env="MINIO_BUCKET")
    minio_secure: bool = Field(False, env="MINIO_SECURE")
    
    @property
    def storage_url(self) -> str:
        """Get storage URL for MinIO/S3."""
        protocol = "https" if self.minio_secure else "http"
        return f"{protocol}://{self.minio_endpoint}"
    
    # OpenAI
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: Optional[str] = Field(None, env="JWT_SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Mock Data Control
    use_mock_data: bool = Field(True, env="USE_MOCK_DATA")
    
    # Observability
    jaeger_endpoint: Optional[str] = Field(None, env="JAEGER_ENDPOINT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
