from sys import api_version
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,".")
from api import app

client = TestClient(app)


def test_read_item():
    response = client.get("/api/v1/organization/x00g8")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "org_id": "x00g8",
    }


def test_read_inexistent_item():
    response = client.get("/api/v1/organization/x30g5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

