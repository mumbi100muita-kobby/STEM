"""Shared Pytest fixtures. Tests use TestingConfig (SQLite in-memory)."""

import pytest

from stem import create_app
from stem.config import TestingConfig
from stem.extensions import db


@pytest.fixture
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf_app():
    """App with CSRF enabled so we can assert tokens are required."""

    class CsrfTestingConfig(TestingConfig):
        WTF_CSRF_ENABLED = True

    application = create_app(CsrfTestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()
