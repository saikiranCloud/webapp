import requests
import pytest

API_BASE_URL = "http://localhost:5000/v1/user"

def test_create_and_get_user():
    user_data = {
        "username": "user5@test.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User"
    }

    response = requests.post(f"{API_BASE_URL}", json=user_data)
    assert response.status_code == 400

    response = requests.get(f"{API_BASE_URL}/self", auth=("user5@test.com", "testpassword"))
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["email"] == "user5@test.com"
    assert user_info["first_name"] == "Test"
    assert user_info["last_name"] == "User"

def test_update_and_get_user():
    
    updated_data = {
        "password": "newpassword",
        "first_name": "Updated",
        "last_name": "User"
    }
    response = requests.put(f"{API_BASE_URL}/self", json=updated_data, auth=("user5@test.com", "testpassword"))
    assert response.status_code == 204

    response = requests.get(f"{API_BASE_URL}/self", auth=("user5@test.com", "newpassword"))
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["first_name"] == "Updated"
    assert user_info["last_name"] == "User"

if __name__ == "__main__":
    pytest.main([__file__])
