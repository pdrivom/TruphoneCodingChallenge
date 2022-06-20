import json
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,".")
from api import app

client = TestClient(app)
good_sim_card_id = '89440001'
bad_sim_card_id = '89440000'
start = '2020-02-01'
end = '2020-02-02'
every = '1hour'
bad_start = '2020-02-00'
bad_end = '2020-02-00'


def test_read_simcard_usage_pagination():
    """Test if pagination is correctly sized"""

    page = 1
    size = 15
    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end=2020-02-02&every={every}&page={page}&size={size}")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == page
    assert resp["size"] == size
    assert len(resp["items"]) == resp["total"]

def test_read_inexistent_simcard_usage():
    """Test if reading inexistent sim_card_id returns 404 on full request"""

    page = 1
    size = 15
    response = client.get(f"/api/v1/simcard/{bad_sim_card_id}/usage?start={start}&end={end}&every={every}&page={page}&size={size}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"No simcard {bad_sim_card_id} found!"}

def test_read_simcard_usage_inexistent_page():
    """Test if pagination is without page used default parameter"""

    size = 15
    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end={end}&every={every}&size={size}")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == 1
    assert resp["size"] == size

def test_read_simcard_usage_inexistent_page_and_size():
    """Test if pagination is without page and size uses default parameters"""

    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end={end}&every={every}")
    assert response.status_code == 200
    resp = response.json()
    assert "items" in resp
    assert "total" in resp
    assert resp["page"] == 1
    assert resp["size"] == 50

def test_read_simcard_usage_bad_every():
    """Test if get 422 on bad parameter 'every'"""

    every = 'hello'
    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end={end}&every={every}")
    assert response.status_code == 422
    assert response.json() == {"detail": f"Query parameter 'every' cannot be {every}. (ex: 1day / 1hour)"}


def test_read_simcard_usage_inexistent_every():
    """Test if get 422 on inexistent parameter 'every'"""

    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end={end}")
    assert response.status_code == 422

def test_read_simcard_usage_bad_start():
    """Test if get 422 on bad parameter 'start'"""

    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={bad_start}&end={end}")
    assert response.status_code == 422

def test_read_simcard_usage_bad_end():
    """Test if get 422 on bad parameter 'end'"""

    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage?start={start}&end={bad_end}")
    assert response.status_code == 422

def test_read_simcard_usage_missing_dates():
    """Test if get 422 if no mandatory parameter"""

    response = client.get(f"/api/v1/simcard/{good_sim_card_id}/usage")
    assert response.status_code == 422