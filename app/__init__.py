from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from .extensions import csrf, db, login_manager, mail, migrate
from .config import Config, TestingConfig, build_runtime_config, load_environment_files


def create_app(test_config: dict | None = None) -> Flask:
    load_environment_files(Path(__file__).resolve().parent.parent)

    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    testing = bool(test_config and test_config.get("TESTING"))
    app.config.from_object(TestingConfig if testing else Config)
    app.config.from_mapping(build_runtime_config(Path(app.instance_path), testing=testing))
    app.config.from_prefixed_env()

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "You must be logged in to view that page."
    mail.init_app(app)
    migrate.init_app(app, db)

    from .auth import auth_bp
    from .forms import LogoutForm
    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_logout_form() -> dict[str, LogoutForm]:
        return {"logout_form": LogoutForm()}

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error: CSRFError) -> tuple[str, int]:
        return (
            render_template(
                "csrf_error.html",
                title="Request expired",
                reason=error.description,
            ),
            400,
        )

    return app
