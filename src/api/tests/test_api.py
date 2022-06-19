from sys import api_version
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,".")
from api import app

client = TestClient(app)


def test_read_organization():
    org_id = 'x00g8'
    response = client.get(f"/api/v1/organization/{org_id}")
    assert response.status_code == 200
    assert response.json()["org_id"] == org_id

def test_read_inexistent_organization():
    org_id = 'x30g5'
    response = client.get(f"/api/v1/organization/{org_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"No organization {org_id} found!"}

def test_read_simcard():
    sim_card_id = '89440001'
    response = client.get(f"/api/v1/simcard/{sim_card_id}")
    assert response.status_code == 200
    assert response.json()["sim_card_id"] == sim_card_id


def test_read_inexistent_simcard():
    response = client.get("/api/v1/simcard/89440000")
    assert response.status_code == 404
    assert response.json() == {"detail": "No simcard 89440000 found!"}

def test_read_simcard_usage_parameters():
    page = 1
    size = 15
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day&page={page}&size={size}")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["page"] == page
    assert response.json()["size"] == size

def test_read_simcard_usage_missing_page():
    size = 15
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day&size={size}")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["size"] == size

def test_read_simcard_usage_missing_page_and_size():
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every=1day")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert response.json()["page"] == 1
    assert response.json()["size"] == 50

def test_read_simcard_usage_bad_every():
    every = 'hello'
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}

def test_read_simcard_usage_bad_every():
    every = 'hello'
    response = client.get(f"api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}

def test_read_simcard_usage_missing_every():
    response = client.get("api/v1/simcard/89440001/usage?start=2020-02-01&end=2020-02-01")
    assert response.status_code == 422

def test_read_simcard_usage_bad_end():
    response = client.get("api/v1/simcard/89440001/usage?start=2020-01-02&end=2020-02-00")
    assert response.status_code == 422

def test_read_simcard_usage_missing_dates():
    response = client.get("api/v1/simcard/89440001/usage")
    assert response.status_code == 422
