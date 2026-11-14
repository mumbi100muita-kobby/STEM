"""Authenticated-route protection and CSRF on mutating requests."""


def test_dashboard_redirects_anonymous_users_to_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_home_redirects_anonymous_users_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_authenticated_user_can_open_dashboard(client):
    client.post(
        "/register",
        data={
            "email": "one@example.com",
            "password": "securepass",
            "confirm_password": "securepass",
        },
        follow_redirects=True,
    )
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Student dashboard" in response.data
    assert b"one@example.com" in response.data


def test_dashboard_is_protected_after_logout(client):
    client.post(
        "/register",
        data={
            "email": "one@example.com",
            "password": "securepass",
            "confirm_password": "securepass",
        },
        follow_redirects=True,
    )
    client.post("/logout")
    response = client.get("/dashboard", follow_redirects=True)
    assert b"Log in to S.T.E.M." in response.data
    assert b"Student dashboard" not in response.data


def test_register_post_without_csrf_token_is_rejected(csrf_app):
    client = csrf_app.test_client()
    response = client.post(
        "/register",
        data={
            "email": "csrf@example.com",
            "password": "securepass",
            "confirm_password": "securepass",
        },
    )
    assert response.status_code == 400


def test_logout_post_without_csrf_token_is_rejected(csrf_app):
    client = csrf_app.test_client()
    response = client.post("/logout")
    assert response.status_code in {400, 302}
    if response.status_code == 302:
        assert "/login" in response.headers["Location"]
