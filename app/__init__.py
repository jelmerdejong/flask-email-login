import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from . import routes
        from . import auth

        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)

        db.create_all()

        return app
