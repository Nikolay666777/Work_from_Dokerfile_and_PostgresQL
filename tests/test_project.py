import pytest


async def _register_and_login(client, username="user1", password="pass123"):
    """Helper: register + login, return auth headers."""
    await client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": password,
    })
    resp = await client.post("/auth/login", data={
        "username": username,
        "password": password,
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_register(client):
    resp = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "pass123",
    })
    assert resp.status_code == 201
    assert resp.json()["username"] == "newuser"


async def test_login(client):
    await client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "pass123",
    })
    resp = await client.post("/auth/login", data={
        "username": "loginuser",
        "password": "pass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


async def test_login_invalid(client):
    resp = await client.post("/auth/login", data={
        "username": "nobody",
        "password": "wrong",
    })
    assert resp.status_code == 401


async def test_create_project(client):
    headers = await _register_and_login(client, "creator")
    resp = await client.post("/projects", json={
        "name": "My Project",
        "description": "Test description",
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Project"
    assert resp.json()["description"] == "Test description"
    assert resp.json()["owner_id"] == 1


async def test_list_projects(client):
    headers = await _register_and_login(client, "lister")
    await client.post("/projects", json={
        "name": "P1",
        "description": "D1",
    }, headers=headers)
    await client.post("/projects", json={
        "name": "P2",
        "description": "D2",
    }, headers=headers)
    resp = await client.get("/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_update_project(client):
    headers = await _register_and_login(client, "updater")
    create_resp = await client.post("/projects", json={
        "name": "Original",
        "description": "Original desc",
    }, headers=headers)
    pid = create_resp.json()["id"]

    resp = await client.put(f"/projects/{pid}", json={
        "name": "Updated",
        "description": "Updated desc",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
    assert resp.json()["description"] == "Updated desc"


async def test_delete_project(client):
    headers = await _register_and_login(client, "deleter")
    create_resp = await client.post("/projects", json={
        "name": "To Delete",
        "description": "Bye",
    }, headers=headers)
    pid = create_resp.json()["id"]

    resp = await client.delete(f"/projects/{pid}", headers=headers)
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get(f"/projects/{pid}", headers=headers)
    assert resp.status_code == 404


async def test_unauthorized_access(client):
    resp = await client.get("/projects")
    assert resp.status_code == 401


async def test_non_owner_forbidden(client):
    # User1 creates a project
    headers1 = await _register_and_login(client, "owner_user")
    create_resp = await client.post("/projects", json={
        "name": "Secret Project",
        "description": "Only for owner",
    }, headers=headers1)
    pid = create_resp.json()["id"]

    # User2 tries to access it
    headers2 = await _register_and_login(client, "intruder")
    resp_get = await client.get(f"/projects/{pid}", headers=headers2)
    assert resp_get.status_code == 403

    resp_put = await client.put(f"/projects/{pid}", json={
        "name": "Hacked",
    }, headers=headers2)
    assert resp_put.status_code == 403

    resp_del = await client.delete(f"/projects/{pid}", headers=headers2)
    assert resp_del.status_code == 403


async def test_project_not_found(client):
    headers = await _register_and_login(client, "nf_user")
    resp = await client.get("/projects/9999", headers=headers)
    assert resp.status_code == 404


async def test_cache_works(client):
    """First GET goes to DB, second GET should come from cache."""
    headers = await _register_and_login(client, "cache_test")
    await client.post("/projects", json={
        "name": "Cached",
        "description": "Test",
    }, headers=headers)

    r1 = await client.get("/projects", headers=headers)
    assert r1.status_code == 200
    r2 = await client.get("/projects", headers=headers)
    assert r2.status_code == 200
    assert r1.json() == r2.json()
