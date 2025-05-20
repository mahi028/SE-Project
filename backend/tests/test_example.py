from . import client

# Add tests here.

def test_example_api(client):
    response = client.get('/api/example')
    assert response.status_code == 200
    assert response.json == {"msg": "Hello World!"}

