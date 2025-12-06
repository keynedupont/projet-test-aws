from types import SimpleNamespace
from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.testclient import TestClient

from projet.app.web import get_token_from_cookie, app, COOKIE


def test_get_token_from_cookie_present():
    client = TestClient(app)
    with client:
        client.cookies.set(COOKIE.name, "abc")
        # Construire une Request à partir du client
        scope = {"type": "http", "headers": []}
        request = Request(scope)
        request._cookies = client.cookies  # injection simple pour le test
        assert get_token_from_cookie(request) == "abc"


def test_get_token_from_cookie_absent():
    client = TestClient(app)
    scope = {"type": "http", "headers": []}
    request = Request(scope)
    assert get_token_from_cookie(request) is None
