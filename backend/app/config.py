import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API
    API_TITLE: str = "AI Architectural Design Generator"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_USER: str = os.getenv("DB_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DATABASE_HOST: str = os.getenv("DB_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DB_NAME", "arch_design_db")
    
    @property
    def DATABASE_URL(self) -> str:
        # Try PostgreSQL first, fallback to SQLite for development
        use_sqlite = os.getenv("USE_SQLITE", "True").lower() == "true"
        if use_sqlite:
            db_path = os.getenv("SQLITE_DB_PATH", "arch_design.db")
            return f"sqlite+aiosqlite:///{db_path}"
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Model Configuration
    MODEL_ID: str = "stabilityai/stable-diffusion-2.1"
    CONTROLNET_MODEL_ID: str = "lllyasviel/sd-controlnet-canny"
    DEVICE: str = os.getenv("DEVICE", "cuda")  # cuda or cpu
    DTYPE: str = os.getenv("DTYPE", "float16")  # float16 or float32
    ENABLE_ATTENTION_SLICING: bool = True
    ENABLE_MODEL_CPU_OFFLOAD: bool = False

    # File Paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    GENERATED_IMAGES_DIR: str = os.path.join(UPLOAD_DIR, "generated")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "logs")

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "file://",  # Allow electron/desktop apps
    ]
    # Allow all origins in development mode
    if DEBUG:
        CORS_ORIGINS = ["*"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.GENERATED_IMAGES_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
