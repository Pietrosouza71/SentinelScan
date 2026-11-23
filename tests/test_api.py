from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import create_app


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tmp_path / "test.sqlite3"))


def test_health_and_frontend_are_served(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        health = client.get("/api/health")
        page = client.get("/")
        stylesheet = client.get("/css/styles.css")

    assert health.status_code == 200
    assert health.json() == {"status": "ok", "mode": "inventory-only"}
    assert "SentinelScan" in page.text
    assert stylesheet.status_code == 200


def test_target_requires_explicit_authorization(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/targets",
            json={
                "name": "Laboratório",
                "target": "lab.example",
                "scope_description": "Host de laboratório sob controle da equipe.",
                "authorization_confirmed": False,
            },
        )

    assert response.status_code == 422


def test_authorization_confirmation_must_be_a_boolean(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/targets",
            json={
                "name": "Laboratório",
                "target": "lab.example",
                "scope_description": "Host de laboratório sob controle da equipe.",
                "authorization_confirmed": "yes",
            },
        )

    assert response.status_code == 422


def test_target_is_normalized_and_audited(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/api/targets",
            json={
                "name": "Laboratório",
                "target": " LAB.EXAMPLE. ",
                "scope_description": "Somente o host do ambiente de testes.",
                "exclusions": ["admin.lab.example"],
                "authorization_reference": "ROE-2026-01",
                "authorization_confirmed": True,
            },
        )
        audit = client.get("/api/audit")

    assert created.status_code == 201
    assert created.json()["hostname"] == "lab.example"
    assert created.json()["authorization_confirmed"] is True
    assert audit.status_code == 200
    assert audit.json()[0]["event_type"] == "target.created"


def test_rejects_urls_and_duplicate_active_targets(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        invalid = client.post(
            "/api/targets",
            json={
                "name": "URL",
                "target": "https://lab.example/path",
                "scope_description": "Escopo de teste.",
                "authorization_confirmed": True,
            },
        )
        payload = {
            "name": "Laboratório",
            "target": "lab.example",
            "scope_description": "Host aprovado para o laboratório.",
            "authorization_confirmed": True,
        }
        first = client.post("/api/targets", json=payload)
        duplicate = client.post("/api/targets", json=payload)

    assert invalid.status_code == 422
    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_deactivation_keeps_history_and_removes_target_from_active_list(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/api/targets",
            json={
                "name": "Laboratório",
                "target": "lab.example",
                "scope_description": "Host de laboratório.",
                "authorization_confirmed": True,
            },
        )
        target_id = created.json()["id"]
        deactivated = client.delete(f"/api/targets/{target_id}")
        active_targets = client.get("/api/targets")
        history = client.get("/api/targets?active_only=false")
        audit = client.get("/api/audit")

    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
    assert active_targets.json() == []
    assert len(history.json()) == 1
    assert audit.json()[0]["event_type"] == "target.deactivated"
