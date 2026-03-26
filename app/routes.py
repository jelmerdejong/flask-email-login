from flask import Blueprint, render_template
from flask_login import current_user, login_required


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index() -> str:
    return render_template(
        "index.html",
        title="Passwordless sign-in",
        description="Request a magic login link and access the secure area without a stored password.",
    )


@main_bp.get("/secure")
@login_required
def secure() -> str:
    return render_template(
        "secure.html",
        title="Secure area",
        email=current_user.email,
    )
