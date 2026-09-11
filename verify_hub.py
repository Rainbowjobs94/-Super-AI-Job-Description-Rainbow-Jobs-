from src.hub import app

def test_hub():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

test_hub()
print("Hub verified!")
