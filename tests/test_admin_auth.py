def test_login_with_correct_credentials(client, admin_user):
    response = client.post(
        "/admin/login",
        data={"email": "admin@test.com", "password": "testpass123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    assert "admin_session" in response.cookies


def test_login_with_wrong_password_fails(client, admin_user):
    response = client.post(
        "/admin/login",
        data={"email": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "admin_session" not in response.cookies


def test_login_with_unknown_email_fails(client, db_session):
    response = client.post(
        "/admin/login",
        data={"email": "nobody@test.com", "password": "whatever123"},
    )
    assert response.status_code == 401


def test_protected_route_blocks_anonymous(client):
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_protected_route_allows_admin(client, admin_user):
    client.post(
        "/admin/login",
        data={"email": "admin@test.com", "password": "testpass123"},
    )
    response = client.get("/admin")
    assert response.status_code == 200
    assert "admin@test.com" in response.text


def test_logout_ends_session(client, admin_user):
    client.post(
        "/admin/login",
        data={"email": "admin@test.com", "password": "testpass123"},
    )
    client.post("/admin/logout")

    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303  # blocked again after logout


def test_password_is_stored_hashed(db_session, admin_user):
    assert admin_user.password_hash != "testpass123"
    assert admin_user.password_hash.startswith("$argon2")
