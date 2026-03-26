from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from .email import send_login_link_email
from .extensions import db, login_manager
from .forms import ConfirmLoginForm, LoginForm, SignupForm
from .models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.secure"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user is None:
            flash("Please sign up first.", "warning")
        else:
            try:
                send_login_link_email(user)
            except Exception:
                current_app.logger.exception("Unable to send login email for %s", user.email)
                flash(
                    "We could not send the sign-in link. Check your mail settings and try again.",
                    "danger",
                )
                return redirect(url_for("auth.login"))

            flash("A sign-in link has been sent to your email address.", "info")

        return redirect(url_for("auth.login"))

    return render_template("auth/login.html", title="Email login link", form=form)


@auth_bp.route("/login_token/<token>", methods=["GET", "POST"])
def login_token(token: str) -> str:
    user = User.verify_login_token(token)
    if user is None:
        flash("This login link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    form = ConfirmLoginForm()
    if form.validate_on_submit():
        login_user(user)
        user.mark_logged_in()
        db.session.commit()
        flash("You are now signed in.", "success")
        return redirect(url_for("main.secure"))

    return render_template(
        "auth/login_token.html",
        title="Confirm sign in",
        form=form,
        user=user,
    )


@auth_bp.post("/logout")
@login_required
def logout() -> str:
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.secure"))

    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = User(email=form.email.data)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with that email already exists.", "warning")
            return redirect(url_for("auth.signup"))

        flash("You are registered. Request a sign-in link to continue.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", title="Create account", form=form)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id.isdigit():
        return None
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized() -> str:
    flash("You must be logged in to view that page.", "warning")
    return redirect(url_for("auth.login"))
