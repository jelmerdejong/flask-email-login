from __future__ import annotations

from html import unescape
from pathlib import Path
import re

import pytest

from app import create_app
from app.extensions import db, mail


CSRF_PATTERN = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


@pytest.fixture
def app(tmp_path: Path):
    database_path = tmp_path / "test.db"
    app = create_app(
        {
            "MAIL_DEFAULT_SENDER": "noreply@example.com",
            "MAIL_SUPPRESS_SEND": True,
            "SECRET_KEY": "test-secret-key-with-32-characters",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "TESTING": True,
            "WTF_CSRF_ENABLED": True,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def outbox(app):
    with app.app_context():
        with mail.record_messages() as captured_messages:
            yield captured_messages


@pytest.fixture
def extract_csrf():
    def _extract(response) -> str:
        page = response.get_data(as_text=True)
        match = CSRF_PATTERN.search(page)
        assert match is not None, page
        return unescape(match.group(1))

    return _extract


@pytest.fixture
def post_form(client, extract_csrf):
    def _post(path: str, data: dict[str, str] | None = None, *, follow_redirects: bool = True, source_path: str | None = None):
        form_response = client.get(source_path or path)
        csrf_token = extract_csrf(form_response)
        payload = {"csrf_token": csrf_token}
        if data:
            payload.update(data)
        return client.post(path, data=payload, follow_redirects=follow_redirects)

    return _post
