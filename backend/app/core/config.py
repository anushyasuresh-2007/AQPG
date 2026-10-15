import os
from typing import List, Union
import json
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CANONICAL_DB_PATH = os.path.join(_BACKEND_DIR, "aqpg.db").replace("\\", "/")


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = f"sqlite:///{_CANONICAL_DB_PATH}"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://aqpg.vercel.app",
    ]
    GEMINI_API_KEY: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean in ("sqlite:///./aqpg.db", "sqlite:///aqpg.db"):
                return f"sqlite:///{_CANONICAL_DB_PATH}"
            return v_clean
        return v

    @model_validator(mode="after")
    def validate_production_database(self) -> "Settings":
        """Fail fast if production environment lacks an external DATABASE_URL or attempts SQLite."""
        if self.ENVIRONMENT.lower() == "production":
            db_url = (self.DATABASE_URL or "").strip()
            if not db_url or db_url.startswith("sqlite"):
                raise ValueError(
                    "Production environment requires an external DATABASE_URL (e.g. mysql+mysqlconnector:// or postgresql://). "
                    f"SQLite database is not permitted in production (got: '{db_url}')."
                )
        return self

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                origins = []
            elif v.startswith("[") and v.endswith("]"):
                try:
                    origins = json.loads(v)
                except Exception:
                    origins = [i.strip() for i in v.split(",") if i.strip()]
            else:
                origins = [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            origins = list(v)
        else:
            origins = []

        default_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://aqpg.vercel.app",
        ]
        for o in default_origins:
            if o not in origins:
                origins.append(o)
        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
