from sys import api_version
from fastapi.testclient import TestClient
from .api import app

client = TestClient(app)


def test_read_item():
    response = client.get("/items/foo")
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "title": "Foo",
        "description": "There goes my hero",
    }


def test_read_inexistent_item():
    response = client.get("/items/baz")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

