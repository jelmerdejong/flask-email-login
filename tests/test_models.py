from __future__ import annotations

from app.extensions import db
from app.models import User


def test_login_token_round_trip(app) -> None:
    with app.app_context():
        user = User(email="token@example.com")
        db.session.add(user)
        db.session.commit()

        token = user.get_login_token()
        verified_user = User.verify_login_token(token)

        assert verified_user is not None
        assert verified_user.id == user.id


def test_expired_login_token_returns_none(app) -> None:
    with app.app_context():
        user = User(email="expired@example.com")
        db.session.add(user)
        db.session.commit()

        expired_token = user.get_login_token(expires_in=-1)

        assert User.verify_login_token(expired_token) is None
