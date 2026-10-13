from unittest.mock import patch
from app.diagnostics.network import NetworkRequest, run_network


def payload():
    return {
        "title": "Internet unavailable",
        "description": "DNS lookup fails",
        "category": "Network",
        "priority": "High",
        "status": "Open",
    }


def test_health(client):
    assert client.get("/api/v1/health").json()["status"] == "ok"


def test_system_demo(client):
    r = client.get("/api/v1/diagnostics/system?demo=true")
    assert r.status_code == 200 and r.json()["device_id"] == "demo-device"


def test_network_validation(client):
    assert (
        client.post(
            "/api/v1/diagnostics/network", json={"hostname": "bad host; rm -rf /", "port": 80}
        ).status_code
        == 422
    )


def test_network_mocked():
    with (
        patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 0))]),
        patch("socket.create_connection"),
    ):
        data = run_network(NetworkRequest(hostname="example.com", port=443))
        assert all(x["status"] == "OK" for x in data["results"])


def test_incident_lifecycle_and_reports(client):
    created = client.post("/api/v1/incidents", json=payload())
    assert created.status_code == 201
    iid = created.json()["id"]
    assert (
        client.patch(f"/api/v1/incidents/{iid}", json={"status": "In Progress"}).status_code == 200
    )
    note = client.post(
        f"/api/v1/incidents/{iid}/notes",
        json={"action": "Checked DNS", "result": "Failed", "next_step": "Review resolver"},
    )
    assert note.status_code == 201
    assert client.get("/api/v1/incidents?status=In%20Progress").json()["total"] == 1
    report = client.get(f"/api/v1/reports/{iid}.json")
    assert report.status_code == 200 and "password" not in report.text.lower()
    assert client.get(f"/api/v1/reports/{iid}.md").status_code == 200
    assert client.delete(f"/api/v1/incidents/{iid}").status_code == 204


def test_not_found(client):
    assert client.get("/api/v1/incidents/999").status_code == 404
