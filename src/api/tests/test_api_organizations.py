import json
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,".")
from api import app

client = TestClient(app)

good_org_id = 'x00g8'
bad_org_id = 'x30g5'


def test_read_organization_usage_pagination():
    """Test if pagination is correctly sized"""

    page = 1
    size = 15
    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-02-01&end=2020-02-02&every=1day&page={page}&size={size}")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == page
    assert resp["size"] == size
    assert len(resp["items"]) == resp["total"]

def test_read_inexistent_organization_usage():
    """Test if reading inexistent org_id returns 404 on full request"""

    page = 1
    size = 15
    response = client.get(f"api/v1/organization/{bad_org_id}/usage?start=2020-02-01&end=2020-02-01&every=1day&page={page}&size={size}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"No organization {bad_org_id} found!"}

def test_read_organization_usage_inexistent_page():
    """Test if pagination is without page used default parameter"""

    size = 15
    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-02-01&end=2020-02-01&every=1hour&size={size}")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == 1
    assert resp["size"] == size

def test_read_organization_usage_inexistent_page_and_size():
    """Test if pagination is without page and size uses default parameters"""

    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-02-01&end=2020-02-01&every=1hour")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == 1
    assert resp["size"] == 50

def test_read_organization_usage_bad_every():
    """Test if get 422 on bad parameter 'every'"""

    every = 'hello'
    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-02-01&end=2020-02-01&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}


def test_read_organization_usage_inexistent_every():
    """Test if get 422 on inexistent parameter 'every'"""

    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-02-01&end=2020-02-01")
    assert response.status_code == 422

def test_read_organization_usage_bad_start():
    """Test if get 422 on bad parameter 'start'"""

    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-01-00&end=2020-02-01")
    assert response.status_code == 422

def test_read_organization_usage_bad_end():
    """Test if get 422 on bad parameter 'end'"""

    response = client.get(f"api/v1/organization/{good_org_id}/usage?start=2020-01-02&end=2020-02-00")
    assert response.status_code == 422

def test_read_organization_usage_missing_dates():
    """Test if get 422 if no mandatory parameter"""

    response = client.get(f"api/v1/organization/{good_org_id}/usage")
    assert response.status_code == 422



