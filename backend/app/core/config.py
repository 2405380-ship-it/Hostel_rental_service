import os
import urllib.parse
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HostelShare"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = ""

    # JWT Authentication
    JWT_SECRET: str = "dev_super_secret_hostelshare_jwt_key_98234710923"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Mock OTP for development/testing
    DEV_MOCK_OTP: str = "123456"

    # CORS
    ALLOWED_ORIGINS: str = "*"
    ALLOWED_ORIGIN_REGEX: str = r"https://.*\.vercel\.app"

    # Supabase Storage Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "hostelshare-media"

    # Brevo (Sendinblue) Email Configuration
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""
    BREVO_SENDER_NAME: str = "HostelShare"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def cors_origins(self) -> List[str]:
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def effective_database_url(self) -> str:
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            url = self.DATABASE_URL.strip().strip("'\"")
            
            # Determine driver prefix
            prefix = ""
            rest = url
            if url.startswith("postgres://"):
                prefix = "postgresql+psycopg2://"
                rest = url[len("postgres://"):]
            elif url.startswith("postgresql://"):
                prefix = "postgresql+psycopg2://"
                rest = url[len("postgresql://"):]
            elif url.startswith("postgresql+psycopg2://"):
                prefix = "postgresql+psycopg2://"
                rest = url[len("postgresql+psycopg2://"):]
            elif url.startswith("sqlite"):
                return url
            else:
                return url

            # Auto-encode special characters in password (e.g. @, #, %)
            if "@" in rest:
                auth_part, host_part = rest.rsplit("@", 1)
                if ":" in auth_part:
                    user, password = auth_part.split(":", 1)
                    unquoted_pw = urllib.parse.unquote(password)
                    quoted_pw = urllib.parse.quote(unquoted_pw, safe="")
                    return f"{prefix}{user}:{quoted_pw}@{host_part}"
                return f"{prefix}{rest}"
            return f"{prefix}{rest}"

        # Strict Supabase requirement: no local SQLite fallback
        raise ValueError(
            "DATABASE_URL is not configured! Please provide your Supabase PostgreSQL connection string in .env or Render environment variables."
        )

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
