from __future__ import annotations

from app.models import User


def create_user(app, post_form, email: str) -> None:
    response = post_form("/signup", {"email": email})
    assert response.status_code == 200

    with app.app_context():
        assert User.find_by_email(email) is not None


def login_with_token(app, post_form, email: str) -> tuple[int, str]:
    with app.app_context():
        user = User.find_by_email(email)
        assert user is not None
        token = user.get_login_token()
        user_id = user.id

    response = post_form(f"/login_token/{token}", source_path=f"/login_token/{token}")
    assert response.status_code == 200
    return user_id, token


def test_home_page_renders(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Passwordless sign-in" in response.get_data(as_text=True)


def test_secure_requires_login(client) -> None:
    response = client.get("/secure")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_signup_creates_a_user(app, post_form) -> None:
    response = post_form("/signup", {"email": "new@example.com"})

    assert "You are registered." in response.get_data(as_text=True)
    with app.app_context():
        assert User.find_by_email("new@example.com") is not None


def test_duplicate_signup_is_rejected(app, post_form) -> None:
    create_user(app, post_form, "duplicate@example.com")

    response = post_form("/signup", {"email": "duplicate@example.com"})

    assert "An account with that email already exists." in response.get_data(as_text=True)


def test_login_request_for_unknown_user_shows_signup_message(post_form) -> None:
    response = post_form("/login", {"email": "missing@example.com"})

    assert "Please sign up first." in response.get_data(as_text=True)


def test_login_request_sends_an_email(app, outbox, post_form) -> None:
    create_user(app, post_form, "member@example.com")

    response = post_form("/login", {"email": "member@example.com"})

    assert "A sign-in link has been sent to your email address." in response.get_data(as_text=True)
    assert len(outbox) == 1
    assert outbox[0].recipients == ["member@example.com"]
    assert "/login_token/" in outbox[0].body


def test_invalid_login_token_redirects_to_login(client) -> None:
    response = client.get("/login_token/not-a-real-token", follow_redirects=True)

    assert response.status_code == 200
    assert "invalid or has expired" in response.get_data(as_text=True)


def test_valid_login_token_flow_signs_user_in(app, client, post_form) -> None:
    create_user(app, post_form, "signedin@example.com")

    with app.app_context():
        user = User.find_by_email("signedin@example.com")
        assert user is not None
        token = user.get_login_token()
        user_id = user.id

    confirm_page = client.get(f"/login_token/{token}")
    assert confirm_page.status_code == 200
    assert "Confirm sign in" in confirm_page.get_data(as_text=True)

    response = post_form(f"/login_token/{token}", source_path=f"/login_token/{token}")

    assert response.status_code == 200
    assert "Secure area" in response.get_data(as_text=True)
    assert "signedin@example.com" in response.get_data(as_text=True)
    with client.session_transaction() as session:
        assert session["_user_id"] == str(user_id)
    with app.app_context():
        refreshed_user = User.find_by_email("signedin@example.com")
        assert refreshed_user is not None
        assert refreshed_user.last_login is not None


def test_logout_is_post_only(app, client, post_form) -> None:
    create_user(app, post_form, "logout@example.com")
    login_with_token(app, post_form, "logout@example.com")

    get_response = client.get("/logout")
    assert get_response.status_code == 405

    post_response = post_form("/logout", source_path="/secure")
    assert post_response.status_code == 200
    assert "You have been logged out." in post_response.get_data(as_text=True)


def test_signup_requires_csrf(client) -> None:
    response = client.post("/signup", data={"email": "csrf@example.com"})

    assert response.status_code == 400


def test_login_requires_csrf(client) -> None:
    response = client.post("/login", data={"email": "csrf@example.com"})

    assert response.status_code == 400


def test_login_token_confirmation_requires_csrf(app, client, post_form) -> None:
    create_user(app, post_form, "token-csrf@example.com")

    with app.app_context():
        user = User.find_by_email("token-csrf@example.com")
        assert user is not None
        token = user.get_login_token()

    response = client.post(f"/login_token/{token}")

    assert response.status_code == 400


def test_logout_requires_csrf(app, client, post_form) -> None:
    create_user(app, post_form, "logout-csrf@example.com")
    login_with_token(app, post_form, "logout-csrf@example.com")

    response = client.post("/logout")

    assert response.status_code == 400
