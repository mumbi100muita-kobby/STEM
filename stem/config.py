"""Explicit configuration classes loaded by STEM_CONFIG.

Flask's deprecated FLASK_ENV setting is not used. Choose a class with
STEM_CONFIG=development|testing|production and put secrets in environment
variables (typically via a gitignored .env file).
"""

import os

from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

# Load .env before class attributes read os.getenv. Harmless if .env is absent.
load_dotenv()


class Config:
    """Shared defaults for every environment."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # PostgreSQL is the intended development and production database.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class DevelopmentConfig(Config):
    """Local development against PostgreSQL."""

    DEBUG = True


class TestingConfig(Config):
    """Automated tests: in-memory SQLite so no Postgres server is required.

    StaticPool keeps a single :memory: connection so create_all() and
    requests in the test client share the same schema.
    """

    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key-not-for-production"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }


class ProductionConfig(Config):
    """Deployed environment. DEBUG stays off; cookies should be HTTPS-only."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config_class(name=None):
    """Resolve a config class from STEM_CONFIG or an explicit name."""
    config_name = (name or os.getenv("STEM_CONFIG") or "development").lower()
    try:
        return CONFIG_BY_NAME[config_name]
    except KeyError as exc:
        valid = ", ".join(sorted(CONFIG_BY_NAME))
        raise ValueError(
            f"Unknown STEM_CONFIG {config_name!r}. Expected one of: {valid}."
        ) from exc
