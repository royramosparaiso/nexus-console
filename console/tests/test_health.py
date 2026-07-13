"""Smoke tests — health + empty instances list."""


async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


async def test_instances_list_empty_by_default(client):
    r = await client.get("/instances")
    assert r.status_code == 200
    assert r.json() == []
