from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
TRUTHY_VALUES = {"1", "true", "t", "yes", "on"}


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    TOKEN_TTL_SECONDS = 600
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600


class TestingConfig(Config):
    TESTING = True


def load_environment_files(base_dir: Path = BASE_DIR) -> None:
    for filename in (".env", ".flaskenv"):
        env_file = base_dir / filename
        if env_file.exists():
            load_dotenv(env_file, override=False)


def build_runtime_config(instance_path: Path, *, testing: bool = False) -> dict[str, object]:
    default_database_path = instance_path / ("test.db" if testing else "app.db")
    default_sender = (
        os.getenv("MAIL_DEFAULT_SENDER")
        or os.getenv("MAIL_USERNAME")
        or "noreply@example.com"
    )

    return {
        "MAIL_DEFAULT_SENDER": default_sender,
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
        "MAIL_PORT": int(os.getenv("MAIL_PORT", "25")),
        "MAIL_SERVER": os.getenv("MAIL_SERVER", "localhost"),
        "MAIL_SUPPRESS_SEND": env_to_bool("MAIL_SUPPRESS_SEND", default=testing),
        "MAIL_USE_SSL": env_to_bool("MAIL_USE_SSL", default=False),
        "MAIL_USE_TLS": env_to_bool("MAIL_USE_TLS", default=False),
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "PREFERRED_URL_SCHEME": os.getenv("PREFERRED_URL_SCHEME", "http"),
        "SECRET_KEY": os.getenv(
            "SECRET_KEY",
            "dev-secret-key-change-me-and-use-a-real-secret",
        ),
        "SQLALCHEMY_DATABASE_URI": normalize_database_url(default_database_path),
    }


def normalize_database_url(default_database_path: Path) -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return f"sqlite:///{default_database_path}"

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def env_to_bool(name: str, *, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_VALUES
