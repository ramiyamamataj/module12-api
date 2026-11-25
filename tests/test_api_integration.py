from faker import Faker
from app.models.calculation import Calculation
from app.models.user import User

fake = Faker()


def create_authenticated_user(client):
    username = fake.user_name() + str(fake.random_int(100, 999))
    email = fake.email()
    password = "Password123!"

    reg_res = client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_res.status_code == 201

    login_res = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return username, email, password, headers


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_user_register_login_and_db_persistence(client, db_session):
    username, email, password, headers = create_authenticated_user(client)

    db_user = db_session.query(User).filter(User.username == username).first()
    assert db_user is not None
    assert db_user.email == email
    assert db_user.last_login is not None

    me_res = client.get("/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == username

    oauth_res = client.post(
        "/users/token",
        data={"username": username, "password": password},
    )
    assert oauth_res.status_code == 200
    assert "access_token" in oauth_res.json()


def test_duplicate_registration_and_invalid_login(client):
    username, email, password, _ = create_authenticated_user(client)

    dup_res = client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert dup_res.status_code == 400

    bad_login = client.post(
        "/users/login",
        json={"username": username, "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401


def test_calculation_bread_lifecycle(client, db_session):
    _, _, _, headers = create_authenticated_user(client)

    # Add (POST /calculations)
    add_res = client.post(
        "/calculations",
        json={"type": "add", "inputs": [12, 8]},
        headers=headers,
    )
    assert add_res.status_code == 201
    created = add_res.json()
    assert created["result"] == 20.0
    calc_id = created["id"]

    # Browse (GET /calculations)
    browse_res = client.get("/calculations", headers=headers)
    assert browse_res.status_code == 200
    assert len(browse_res.json()) == 1

    # Read (GET /calculations/{id})
    read_res = client.get(f"/calculations/{calc_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["id"] == calc_id

    # Edit (PUT /calculations/{id}) - updates both type and inputs
    edit_res = client.put(
        f"/calculations/{calc_id}",
        json={"type": "multiply", "inputs": [6, 7]},
        headers=headers,
    )
    assert edit_res.status_code == 200
    assert edit_res.json()["type"] == "multiply"
    assert edit_res.json()["result"] == 42.0

    # Delete (DELETE /calculations/{id})
    del_res = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert del_res.status_code == 204

    missing_res = client.get(f"/calculations/{calc_id}", headers=headers)
    assert missing_res.status_code == 404
    assert db_session.query(Calculation).count() == 0


def test_calculation_validation_and_unauthorized_access(client):
    unauth = client.get("/calculations")
    assert unauth.status_code == 401

    _, _, _, headers = create_authenticated_user(client)

    div_zero = client.post(
        "/calculations",
        json={"type": "divide", "inputs": [10, 0]},
        headers=headers,
    )
    assert div_zero.status_code == 422

    bad_type = client.post(
        "/calculations",
        json={"type": "power", "inputs": [2, 3]},
        headers=headers,
    )
    assert bad_type.status_code == 422
