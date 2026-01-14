from fastapi.testclient import TestClient

from fin_control.app import app

client = TestClient(app)

def test_deve_retornar_hello_world():
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'Hello World!'}