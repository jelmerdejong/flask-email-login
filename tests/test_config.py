from __future__ import annotations

import os
from pathlib import Path

from app.config import build_runtime_config, load_environment_files


def test_load_environment_files_keeps_existing_environment_values(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / ".env").write_text("SECRET_KEY=from-file\nMAIL_PORT=2525\n", encoding="utf-8")
    monkeypatch.setenv("SECRET_KEY", "from-environment")
    monkeypatch.delenv("MAIL_PORT", raising=False)

    load_environment_files(tmp_path)

    assert os.getenv("SECRET_KEY") == "from-environment"
    assert os.getenv("MAIL_PORT") == "2525"


def test_build_runtime_config_prefers_database_url_environment_variable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/example")

    config = build_runtime_config(tmp_path)

    assert config["SQLALCHEMY_DATABASE_URI"] == "postgresql://user:pass@localhost:5432/example"
