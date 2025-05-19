import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
import pytest

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

def test_example_api(client):
    response = client.get('/api/example')
    assert response.status_code == 200
    assert response.json == {"msg": "Hello World!"}
    