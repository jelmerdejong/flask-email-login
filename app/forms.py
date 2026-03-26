from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from .models import User


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return value
    return value.strip().lower()


class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        filters=[normalize_email],
        validators=[DataRequired(), Email(), Length(max=320)],
        render_kw={"autocomplete": "email", "placeholder": "you@example.com"},
    )
    submit = SubmitField("Create account")

    def validate_email(self, field: StringField) -> None:
        if User.find_by_email(field.data):
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        filters=[normalize_email],
        validators=[DataRequired(), Email(), Length(max=320)],
        render_kw={"autocomplete": "email", "placeholder": "you@example.com"},
    )
    submit = SubmitField("Email login link")


class ConfirmLoginForm(FlaskForm):
    submit = SubmitField("Continue to secure area")


class LogoutForm(FlaskForm):
    submit = SubmitField("Log out")
