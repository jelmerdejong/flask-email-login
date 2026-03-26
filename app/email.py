from __future__ import annotations

from flask import current_app, render_template, url_for
from flask_mail import Message

from .extensions import mail
from .models import User


def send_login_link_email(user: User) -> Message:
    login_url = url_for("auth.login_token", token=user.get_login_token(), _external=True)
    message = Message(
        subject="Your sign-in link",
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        body=render_template("email/login.txt", user=user, login_url=login_url),
        html=render_template("email/login.html", user=user, login_url=login_url),
    )

    current_app.logger.info("Magic login link for %s: %s", user.email, login_url)
    mail.send(message)
    return message
