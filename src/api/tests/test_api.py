from sys import api_version
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,".")
from api import app

client = TestClient(app)


def test_read_organization():
    # since this response is known, verification can be made
    response = client.get("/api/v1/organization/x00g8")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "org_id": "x00g8",
    }

def test_read_inexistent_organization():
    # since this response is known, verification can be made
    response = client.get("/api/v1/organization/x30g5")
    assert response.status_code == 404
    assert response.json() == {"detail": "No organization x30g5 found!"}

def test_read_simcard():
    # since this response is known, verification can be made
    response = client.get("/api/v1/organization/x00g8")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "org_id": "x00g8",
    }

def test_read_inexistent_simcard():
    # since this response is known, verification can be made
    response = client.get("/api/v1/simcard/89440000")
    assert response.status_code == 404
    assert response.json() == {"detail": "No simcard 89440000 found!"}

def test_read_simcard_usage_parameters():
    # since this response is known, verification can be made
    page = 1
    size = 15
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day&page={page}&size={size}")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["page"] == page
    assert response.json()["size"] == size

def test_read_simcard_usage_missing_page():
    # since this response is known, verification can be made
    size = 15
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day&size={size}")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["size"] == size

def test_read_simcard_usage_missing_page_and_size():
    # since this response is known, verification can be made
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["page"] == 1
    assert response.json()["size"] == 50

def test_read_simcard_usage_bad_every():
    # since this response is known, verification can be made
    every = 'hello'
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}

def test_read_simcard_usage_bad_every():
    # since this response is known, verification can be made
    every = 'hello'
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}

def test_read_simcard_usage_missing_every():
    # since this response is known, verification can be made
    response = client.get("api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01")
    assert response.status_code == 422

def test_read_simcard_usage_bad_end():
    # since this response is known, verification can be made
    response = client.get("api/v1/simcard/89440001/usage?start=2020-01-02&end=2020-02-00")
    assert response.status_code == 422

def test_read_simcard_usage_missing_dates():
    # since this response is known, verification can be made
    response = client.get("api/v1/simcard/89440001/usage")
    assert response.status_code == 422
