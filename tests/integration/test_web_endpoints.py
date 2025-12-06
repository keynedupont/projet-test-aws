import pytest
from fastapi.testclient import TestClient
from projet.app.web import app


def test_public_pages_render():
    with TestClient(app) as client:
        for path in ["/", "/login", "/signup"]:
            r = client.get(path)
            assert r.status_code == 200


def test_dashboard_requires_auth(monkeypatch):
    with TestClient(app) as client:
        r = client.get("/dashboard", follow_redirects=False)
        # redirection vers /login si non authentifié
        assert r.status_code in (302, 303)
