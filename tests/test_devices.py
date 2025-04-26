import pytest
from app import create_app
import os

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    return {
        'Authorization': f'Bearer {os.getenv("TEST_API_KEY", "test-api-key-1")}'
    }

def test_health_check(client):
    response = client.get('/v1/devices/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_register_device(client, auth_headers):
    # Test registering a new device
    response = client.put(
        '/v1/devices/test-user/test-device',
        json={
            'platform': 'ios',
            'token': 'test-token'
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json
    assert data['user_id'] == 'test-user'
    assert data['device_id'] == 'test-device'
    assert data['platform'] == 'ios'
    assert data['token'] == 'test-token'

def test_get_device(client, auth_headers):
    # First register a device
    client.put(
        '/v1/devices/test-user/test-device',
        json={
            'platform': 'ios',
            'token': 'test-token'
        },
        headers=auth_headers
    )

    # Then get it
    response = client.get(
        '/v1/devices/test-user/test-device',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json
    assert data['user_id'] == 'test-user'
    assert data['device_id'] == 'test-device'

def test_list_devices(client, auth_headers):
    # First register a device
    client.put(
        '/v1/devices/test-user/test-device',
        json={
            'platform': 'ios',
            'token': 'test-token'
        },
        headers=auth_headers
    )

    # Then list devices
    response = client.get(
        '/v1/devices/test-user',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['user_id'] == 'test-user'

def test_delete_device(client, auth_headers):
    # First register a device
    client.put(
        '/v1/devices/test-user/test-device',
        json={
            'platform': 'ios',
            'token': 'test-token'
        },
        headers=auth_headers
    )

    # Then delete it
    response = client.delete(
        '/v1/devices/test-user/test-device',
        headers=auth_headers
    )
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(
        '/v1/devices/test-user/test-device',
        headers=auth_headers
    )
    assert response.status_code == 404

def test_register_device_missing_fields(client, auth_headers):
    response = client.put(
        '/v1/devices/test-user/test-device',
        json={},
        headers=auth_headers
    )
    assert response.status_code == 400

def test_get_nonexistent_device(client, auth_headers):
    response = client.get(
        '/v1/devices/test-user/nonexistent',
        headers=auth_headers
    )
    assert response.status_code == 404

def test_delete_nonexistent_device(client, auth_headers):
    response = client.delete(
        '/v1/devices/test-user/nonexistent',
        headers=auth_headers
    )
    assert response.status_code == 404 