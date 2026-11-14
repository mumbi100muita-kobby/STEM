"""Registration, login, logout, and password-storage behaviour."""

from stem.extensions import db
from stem.models.user import User
from stem.services.auth_service import AuthError, register_user


def register(client, email="student@example.com", password="securepass"):
    return client.post(
        "/register",
        data={
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="student@example.com", password="securepass"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_register_creates_user_and_lands_on_dashboard(client, app):
    response = register(client)
    assert response.status_code == 200
    assert b"Student dashboard" in response.data
    assert b"student@example.com" in response.data

    with app.app_context():
        user = User.query.filter_by(email="student@example.com").one()
        assert user.password_hash
        assert user.password_hash != "securepass"
        assert "securepass" not in user.password_hash
        assert user.check_password("securepass")


def test_register_normalizes_email_case(client, app):
    register(client, email="Alex@Example.COM")
    with app.app_context():
        assert User.query.filter_by(email="alex@example.com").one()


def test_duplicate_email_is_rejected(client, app):
    register(client)
    client.post("/logout")
    response = register(client)
    assert response.status_code == 200
    assert b"already exists" in response.data
    with app.app_context():
        assert User.query.count() == 1


def test_invalid_email_is_rejected(client, app):
    response = register(client, email="not-an-email")
    assert b"valid email" in response.data
    with app.app_context():
        assert User.query.count() == 0


def test_short_password_is_rejected(client, app):
    response = register(client, password="short")
    assert b"Password must be" in response.data
    with app.app_context():
        assert User.query.count() == 0


def test_register_user_service_hashes_password(app):
    with app.app_context():
        user = register_user("service@example.com", "anotherpass")
        db.session.refresh(user)
        assert user.password_hash != "anotherpass"
        assert user.check_password("anotherpass")
        try:
            register_user("service@example.com", "anotherpass")
            assert False, "duplicate email should raise AuthError"
        except AuthError as exc:
            assert exc.field == "email"


def test_login_succeeds_with_correct_credentials(client):
    register(client)
    client.post("/logout")
    response = login(client)
    assert b"Student dashboard" in response.data
    assert b"You are logged in." in response.data


def test_login_fails_with_wrong_password(client):
    register(client)
    client.post("/logout")
    response = login(client, password="wrongpassword")
    assert b"Invalid email or password" in response.data
    assert b"Student dashboard" not in response.data


def test_login_fails_for_unknown_email(client):
    response = login(client, email="missing@example.com")
    assert b"Invalid email or password" in response.data


def test_logout_ends_session(client):
    register(client)
    response = client.post("/logout", follow_redirects=True)
    assert b"You have been logged out." in response.data
    dashboard = client.get("/dashboard", follow_redirects=True)
    assert b"Log in to S.T.E.M." in dashboard.data
