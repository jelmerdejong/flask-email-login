from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from flask_login import UserMixin
from jwt import InvalidTokenError
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    created_on: Mapped[datetime | None] = mapped_column(
        DateTime(),
        default=datetime.utcnow,
        nullable=True,
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    def get_login_token(self, expires_in: int | None = None) -> str:
        ttl_seconds = expires_in or current_app.config["TOKEN_TTL_SECONDS"]
        payload = {
            "login_token": self.id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        }
        return jwt.encode(
            payload,
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @classmethod
    def verify_login_token(cls, token: str) -> User | None:
        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
        except InvalidTokenError:
            return None

        user_id = payload.get("login_token")
        if not isinstance(user_id, int):
            return None

        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email: str) -> User | None:
        statement = db.select(cls).where(cls.email == email)
        return db.session.scalar(statement)

    def mark_logged_in(self) -> None:
        self.last_login = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User {self.email}>"
